# stressio

## About

This is a rewrite of the [`disk_cpu_load.sh`] utility.  It is faithful to the original's inputs and outputs.

I chose to continue to use the imperative programming style of the original.  However, there is a bit of functional programming sprinkled in, specifically [partial application], where I felt that it made sense.

Partial application is a good choice for this utility because the calculations are dependent upon one another.  For example, as soon as the [`dd`] utility is done reading from the disk device, the program will read again from [`/proc/stats`] and then immediately make its (final) calculations.

I avoided `OOP` paradigms such as classes because I felt it was overkill for such a small program and would negatively impact readability.  The program reads well, with only a small number of helper functions that do one thing and one thing well, as is customary among Unix programs (and the best advice I've ever read about programming and design).

The `compute_cpu_load` function arguably could be further abstracted to cut closer to the Unix philosophy and make testing easier, but I refrained from doing so as to not over-complicate and over-engineer the program.

It only uses the standard library with no external dependencies.

## Installation

```bash
$ git clone git@github.com/btoll/stressio.git
$ cd stressio
$ pip3 install --editable .
```

This will install a "binary" to `$HOME/.local/bin/stressio`.

If `stressio` cannot be found as a command-line tool, make sure that `$HOME/.local/bin` is in your `PATH`.

> Want to know more about how the binary is installed?  Of course you do!  The Python tooling is called `console_scripts`, and you can find a brief introduction and example on [the world's most dangerous website].

## References

- [The Python Standard Library](https://docs.python.org/3/library/)
- [Miscellaneous kernel statistics in /proc/stat](https://docs.kernel.org/filesystems/proc.html#miscellaneous-kernel-statistics-in-proc-stat)
- [The subprocess Module: Wrapping Programs With Python](https://realpython.com/python-subprocess/)

[`disk_cpu_load.sh`]: https://git.launchpad.net/coding-samples/tree/samples/disk_cpu_load.sh
[partial application]: https://docs.python.org/3/library/functools.html#functools.partial
[`dd`]: https://www.man7.org/linux/man-pages/man1/dd.1.html
[`/proc/stats`]: https://docs.kernel.org/filesystems/proc.html#miscellaneous-kernel-statistics-in-proc-stat
[the world's most dangerous website]: https://benjamintoll.com/2021/04/04/on-python-entry_points/#console_scripts

