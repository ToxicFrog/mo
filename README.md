## mo -- a music organizer

mo is a small command line tool for tagging music files, and moving those files into a music library based on their tags, quickly and easy. I wrote it to help me organize my vast and completely disorganized music collection.

It recognizes .flac, .mp3, .mp4, .aac, and .ogg files. It uses FLAC/Vorbis tags for .flac and .ogg files, ID3v2 tags for .mp3 files, and tries to autodetect the rest. Autodetection is very basic and using it may require you to know what the tags are called internally; improved support for other formats will come as I encounter music in my collection that uses them.

It has two modes, `mo tag` and `mo sort`. Basic help on each of them is available with `mo <mode> --help`. This document covers details too lengthy for the built in help.

## rc file

`mo` will read a default configuration from the file `~/.morc` on startup. This is a basic ini file containing (up to) two sections, `[sort]` for settings to apply when sorting, and `[tag]` for settings to apply when tagging.

These settings are applied to the internal configuration variables, rather than parsed as command-line arguments. In particular, this means that:

  * All of the `--prefix` options are configured by setting `file-name`
  * Argument-less flags are set with `flag: true`

For example, my configuration file is:

    [sort]
    library: /music
    file-name: {disc?}{track!d:02d} - {title}
    safe-paths: windows

## mo tag

`mo tag` takes a set of tags to apply and a set of files to apply them to. Tags are specified with `--tag=VALUE` or `--tag?=VALUE` -- the former sets the tag on all files, the latter only on those files that don't have that tag set already. Setting an empty value (`--tag=`) will clear that tag entirely.

It 'naturally' understands the following tags: album, arranger, artist, category, composer, conductor, disc, genre, group, performer, title, and track. Not all of these are 'standard' tags in all formats it supports; in particular 'category' uses the ID3 extension tag `TXXX:TIT0`. ('group' is short for `TIT1`, 'content group'). If you know the exact tag the underlying format uses, you can also use that; for example, you can set an MP3 file's publisher with `--TPUB`.

There is also a special tag, `--auto`, which is used to infer tag values from the filename. This takes, rather a tag value, a pattern to match against the path to the file. The pattern is a "sample" filename, with sections you want extracted into tags written as the tag name enclosed in square brackets, for example:

    mo tag --artist='Kajiura Yuki' --auto='[album]/[track] - [title].mp3'

Internally, it is treated as a regular expression where each `[tag]` is a nongreedy match for one or more non-'/' characters. As with tags as command line options, tags in the pattern can end with '?', in which case they will be matched, but set only if the file does not already have that tag. To match a sequence of characters without placing them in a tag, use `[]`. There is currently no support for literal `[]` characters or more sophisticated regular expression patterns.


## mo sort

`mo sort` is much simpler than `mo tag`; it just takes some fine tuning options (documented in the `--help`) and paths and moves those files into your music library. (The location of that library is one of those tuning options.)

For greater control over the disposition of the files, the `--dir-name` and `--file-name` options can be specified directly. The templates they take are actually Python formatting strings[1], with keys being tags in the files being sorted, or the special tag `{library}` for the library location. There are also convenience functions `--prefix-track`, `--prefix-artist`, and `--prefix-both` to support the common use cases of wanting numbered tracks, filenames with artist and title rather than just title, or both at once. You can also use `--no-prefix` to override any default set in the configuration file (equivalent to `--file-name={title}`).

It has two enhancements over normal python formatting strings: it supports a new conversion format, 'd', for converting to integer (used in the template specified by `--prefix-track`), and it treats tags ending with '?' specially. If those tags (sans '?') are not present in the file being sorted, it treats them as the empty string; if any other tag is missing, it results in an error.

The complete default path for sorting, with `--prefix-both` enabled, is:

    {library}/{genre}/{category?}/{group/artist/composer/performer}/{album}/
        {disc?}{track!d:02d} - {artist} - {title}

Which is to say, it sorts by genre and optional category, then content-group (falling back to artist, then composer, and then performer if there is no content-group set), and then album, then names the files with disc number, two-digit track number, artist name, and title. (Extensions are applied automatically.) If the category name or disc number tags are missing, they are simply skipped; if any other tag is missing, it raises an error.

`mo sort` is also (somewhat) intelligent about the contents of the tags and will strip out characters that are not legal in filenames. The default is to strip out `/` and replace it with `-`; you can change the former with the `--safe-paths` option and the latter with `--safe-char`. `--safe-paths=linux` is equivalent to `--safe-paths=/` and is the default; `--safe-paths=windows` is equivalent to `--safe-paths='<>:"/\|?*'`. All listed characters will be replaced with the `--safe-char`.

Note that this path modification only affects the path it stores the file under, *not* the original tags, which are left unaffected. It also *only* affects path elements read from tags; anything specified directly with `--library`, `--dir-name`, or `--file-name` is used exactly as is.

It is *strongly* recommended that you perform a dry run without actually moving any files first, to make sure everything goes where you expect it to. This is the default behaviour. To actually move the files, use `--go`.

[1] https://docs.python.org/2/library/functions.html#format

## License

Copyright © 2014 Ben "ToxicFrog" Kelly, Google Inc.

Distributed under the Apache License v2; see the file COPYING for details.

### Disclaimer

This is not an official Google product and is not supported by Google.
