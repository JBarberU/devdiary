# DevDiary

Devdiary is a tool for creating daily diary entries for tracking work

It uses a simple folder structure based on:
```bash
devdiary:
  2015:
    04:
      02.md
      04.md
    07:
      04.md
      29.md
      30.md
  2016:
    02:
      02.md
    12:
      24.md
      25.md
```

The default storage location is `~/.devdiary/diaries`, which might be good to keep under version control.

## Usage

The easiest usage is to create an alias like this:
```bash
# Add to your {bash,zsh,whatever}rc:
alias devd="vim $(devdiary.py --add --latest)"
```

This will create a new diary entry if needed, and open it in vim (replace with your favorite editor)

You may also want to use the `--summarize` argument to get a nice summary of your diaries.
```bash
$ devdiary.py --summarize
$ # or to list only specific years:
$ devdiary.py --summarize 2014 2015
```

## License

See [LICENSE](LICENSE.md)

