# Handprint command summary

## Command-line options

The following table summarizes all the command line options available. (Note: on Windows computers, `/` must be used as the prefix character instead of the `-` dash character):

| Short&nbsp;&nbsp;&nbsp;&nbsp;    | Long&nbsp;form | Meaning | Default |  |
|----------------------------------|----------------|---------|---------|--|
| `-a` _A_   | `--add-creds` _A_   | Add credentials for service _A_ and exit | | |
| `-b` _B_   | `--base-name` _B_   | Write outputs to files named _B_-n | Use base names of image files | ⚑ |
| `-C`       | `--no-color`        | Don't color-code info messages | Color-code terminal output |
| `-c`       | `--compare`         | Compare to ground truth; see `-r` too | |
| `-d` _D_   | `--display` _D_     | Display annotation types _D_ | Display text annotations | ★ |
| `-e`       | `--extended`        | Produce extended results | Produce only summary image | |
| `-f` _F_   | `--from-file` _F_   | Read file names or URLs from file _F_ | Use args on the command line |
| `-G`       | `--no-grid`         | Don't create summary image | Create an _N_&times;_N_ grid image| |
| `-h`       | `--help`            | Display help, then exit | | |
| `-j`       | `--reuse-json`      | Reuse prior JSON results if found | Ignore any existing results | | 
| `-l`       | `--list`            | Display known services and exit | | | 
| `-m` _x,y_ | `--text-move` _x,y_ | Move each text annotation by x,y | `0,0` | |
| `-n` _N_   | `--confidence` _N_  | Use confidence score threshold _N_ | `0` | |
| `-o` _O_   | `--output` _O_      | Write all outputs to directory _O_ | Write to images' directories | |
| `-q`       | `--quiet`           | Don't write messages while working | Be chatty while working |
| `-r`       | `--relaxed`         | Use looser criteria for `--compare` | |
| `-s` _S_   | `--service` _S_     | Use recognition service _S_; see `-l` | Use all services | |
| `-t` _T_   | `--threads` _T_     | Use _T_ number of threads | Use (#cores)/2 threads | |
| `-V`       | `--version`         | Write program version info and exit | | |
| `-x` _X_   | `--text-color` _X_  | Use color _X_ for text annotations | Red | |
| `-z` _Z_   | `--text-size` _Z_   | Use font size _Z_ for text annotations | Use font size 12 | |
| `-@` _OUT_ | `--debug` _OUT_     | Write detailed execution info to _OUT_ | Normal mode | ⬥ |

⚑ &nbsp; If URLs are given, then the outputs will be written by default to names of the form `document-n`, where n is an integer.  Examples: `document-1.jpg`, `document-1.handprint-google.txt`, etc.  This is because images located in network content management systems may not have any clear names in their URLs.<br>
★ &nbsp; The possible values of _D_ are: `text`, `bb`, `bb-word`, `bb-line`, `bb-para`. Multiple values must be separated with commas. The value `bb` is a shorthand for `bb-word,bb-line,bb-para`. The default is `text`.<br>
⬥ &nbsp; To write to the console, use the character `-` as the value of _OUT_; otherwise, _OUT_ must be the name of a file where the output should be written.


## Return values

This program exits with a return code of 0 if no problems are encountered.  It returns a nonzero value otherwise. The following table lists the possible return values:

| Code | Meaning                                                  |
|:----:|----------------------------------------------------------|
| 0    | success &ndash; program completed normally               |
| 1    | the user interrupted the program's execution             |
| 2    | encountered a bad or missing value for an option         |
| 3    | no network detected &ndash; cannot proceed               |
| 4    | file error &ndash; encountered a problem with a file     |
| 5    | server error &ndash; encountered a problem with a server |
| 6    | an exception or fatal error occurred                     |
