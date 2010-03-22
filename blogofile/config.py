#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This loads the user's _config.py file and provides a standardized interface
into it."""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Tue Jul 28 20:40:29 2009"

import os
import post
import util
import writer
import blogofile_bf as bf

__loaded = False

class UnknownConfigSectionException(Exception):
    pass
class ConfigNotFoundException(Exception):
    pass

override_options = {} #override config options (mostly from unit tests)

default_config = r"""######################################################################
# This is the main Blogofile configuration file.
# www.Blogofile.com
#
# This file has the following ordered sections:
#  * Basic Settings
#  * Intermediate Settings
#  * Advanced Settings
#
#  You really only _need_ to change the Basic Settings.
######################################################################

######################################################################
# Basic Settings
#  (almost all sites will want to configure these settings)
######################################################################
## site_url -- Your site's full URL
# Your "site" is the same thing as your _site directory.
#  If you're hosting a blogofile powered site as a subdirectory of a larger
#  non-blogofile site, then you would set the site_url to the full URL
#  including that subdirectory: "http://www.yoursite.com/path/to/blogofile-dir"
site_url         = "http://www.yoursite.com"

#### Blog Settings ####

## blog_enabled -- Should the blog be enabled?
#  (You don't _have_ to use blogofile to build blogs)
blog_enabled = True

## blog_path -- Blog path.
#  This is the path of the blog relative to the site_url.
#  If your site_url is "http://www.yoursite.com/~ryan"
#  and you set blog_path to "/blog" your full blog URL would be
#  "http://www.yoursite.com/~ryan/blog"
#  Leave blank "" to set to the root of site_url
blog_path = "/blog"

## blog_name -- Your Blog's name.
# This is used repeatedly in default blog templates
blog_name        = "Your Blog's Name"

## blog_description -- A short one line description of the blog
# used in the RSS/Atom feeds.
blog_description = "Your Blog's short description"

## blog_timezone -- the timezone that you normally write your blog posts from
blog_timezone    = "US/Eastern"

## blog_posts_per_page -- Blog posts per page
blog_posts_per_page = 5

# Automatic Permalink
# (If permalink is not defined in post article, it's generated
#  automatically based on the following format:)
# Available string replacements:
# :year, :month, :day -> post's date
# :title              -> post's title
# :uuid               -> sha hash based on title
# :filename           -> article's filename without suffix
blog_auto_permalink_enabled = True
# This is relative to site_url
blog_auto_permalink         = "/blog/:year/:month/:day/:title"

######################################################################
# Intermediate Settings
######################################################################
#### Disqus.com comment integration ####
disqus_enabled = False
disqus_name    = "your_disqus_name"

#### Emacs Integration ####
emacs_orgmode_enabled = False
# emacs binary (orgmode must be installed)
emacs_binary    = "/usr/bin/emacs"               # emacs 22 or 23 is recommended
emacs_preload_elisp = "_emacs/setup.el"          # preloaded elisp file
emacs_orgmode_preamble = r"#+OPTIONS: H:3 num:nil toc:nil \n:nil"   # added in preamble

#### Blog post syntax highlighting ####
syntax_highlight_enabled = True
# You can change the style to any builtin Pygments style
# or, make your own: http://pygments.org/docs/styles
syntax_highlight_style   = "murphy"

#### Custom blog index ####
# If you want to create your own index page at your blog root
# turn this on. Otherwise blogofile assumes you want the
# first X posts displayed instead
blog_custom_index = False

#### Post excerpts ####
# If you want to generate excerpts of your posts in addition to the
# full post content turn this feature on
post_excerpt_enabled     = True
post_excerpt_word_length = 25
#Also, if you don't like the way the post excerpt is generated
#You can define a new function
#below called post_excerpt(content, num_words)

#### Blog pagination directory ####
# blogofile places extra pages of your blog in
# a secondary directory like the following:
# http://www.yourblog.com/blog_root/page/4
# You can rename the "page" part here:
blog_pagination_dir = "page"

#### Blog category directory ####
# blogofile places extra pages of your or categories in
# a secondary directory like the following:
# http://www.yourblog.com/blog_root/category/your-topic/4
# You can rename the "category" part here:
blog_category_dir = "category"

#### Site css directory ####
# Where to write css files generated by blogofile
# (eg, Syntax highlighter writes out a pygments.css file)
# This is relative to site_url
site_css_dir = "/css"

#### Post encoding ####
blog_post_encoding = "utf-8"

######################################################################
# Advanced Settings
######################################################################
# These are the default ignore patterns for excluding files and dirs
# from the _site directory
# These can be strings or compiled patterns.
# Strings are assumed to be case insensitive.
file_ignore_patterns = [
    r".*([\/]|[\\])_.*",    #All files that start with an underscore
    r".*([\/]|[\\])#.*",    #Emacs temporary files
    r".*~$",                #Emacs temporary files
    r".*([\/]|[\\])\.git$", #Git VCS dir
    r".*([\/]|[\\])\.hg$",  #Mercurial VCS dir
    r".*([\/]|[\\])\.bzr$", #Bazaar VCS dir
    r".*([\/]|[\\])\.svn$", #Subversion VCS dir
    r".*([\/]|[\\])CVS$"    #CVS dir
    ]

#### Default post filters ####
# If a post does not specify a filter chain, use the 
# following defaults based on the post file extension:
blog_post_default_filters = {
    "markdown": "syntax_highlight, markdown",
    "textile": "syntax_highlight, textile",
    "org": "syntax_highlight, org"
}

### Pre/Post build hooks:
def pre_build():
    #Do whatever you want before the _site is built
    pass
def post_build():
    #Do whatever you want after the _site is built
    pass
"""

def recompile():
    #Compile file_ignore_patterns
    import re
    global compiled_file_ignore_patterns
    compiled_file_ignore_patterns = []
    for p in file_ignore_patterns:
        if isinstance(p,basestring):
            compiled_file_ignore_patterns.append(re.compile(p,re.IGNORECASE))
        else:
            #p could just be a pre-compiled regex
            compiled_file_ignore_patterns.append(p)
    import urlparse
    global blog_url
    blog_url = urlparse.urljoin(site_url,blog_path)
        
def __load_config(path=None):
    #Strategy: Load the default config, and then the user's config.
    #This will make sure that we have good default values if the user's
    #config is missing something.
    exec(default_config)
    if path:
        execfile(path)
    #config is now in locals() but needs to be in globals()
    for k,v in locals().items():
        globals()[k] = v
    #Override any options (from unit tests)
    for k,v in override_options.items():
        globals()[k] = v
    recompile()
    __loaded = True
    
def init(config_file_path=None):
    #Initialize the config, if config_file_path is None,
    #just load the default config
    if config_file_path:
        if not os.path.isfile(config_file_path):
            raise ConfigNotFoundException
        __load_config(config_file_path)
    else:
        __load_config()
    return globals()['__name__']
