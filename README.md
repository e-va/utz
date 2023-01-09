# μ time zone (library)

An embedded timezone library and ~3kB tzinfo database featuring nearly
all current timezones present in the IANA timezone database.
Designed for use on budget embedded systems with low program space.

The C header containing packed timezone information is generated from
the IANA timezone database.

## Tradeoffs

All historical timezone information has been pruned to save space.

A limited number of aliases are available. (by default restricted to the
same set that android uses) In cases where the alias is not available,
the standard time UTC offset and abbreviation (if present) will be
displayed.

This library is generally inflexible as it heavily relies on
assumptions pertaining to timezone offset increments, abbreviation
formatting, etc to make efficient use of bit packs.

## Limitations

The current utility library does not support parsing /
packing all possible syntax of the source IANA tz database.
Instead a subset corresponding to the what is needed to correctly parse  
most zones is implemented.

## Links

[zic man page and IANA tz database format documentation](https://linux.die.net/man/8/zic)

[vendored files](./vendor)

## Environment

Works with Python 3.6.

Python 3.8 gives an error when executing `compile_tzlinks.py`:
```bash
$ python utils/compile_tzlinks.py
Traceback (most recent call last):
  File "utils/compile_tzlinks.py", line 53, in <module>
    main()
  File "utils/compile_tzlinks.py", line 16, in main
    tz = tzwhere.tzwhere()
  File "utz/venv/lib/python3.8/site-packages/tzwhere/tzwhere.py", line 62, in __init__
    self.timezoneNamesToPolygons[tzname] = WRAP(polys)
ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 2 dimensions. The detected shape was (1, 2) + inhomogeneous part.
```

## Instructions to generate files (without Make)

1. Setup dev environment:

```bash
$ python3.6 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

2. Generate links based on major cities:

   - Using the default input file (`vendor/wikipedia/majorcities.html`): \
   `$ python utils/compile_tzlinks.py`
   - Using the other input file (specify via CLI arg):
     ```bash
     $ python utils/compile_tzlinks.py vendor/wikipedia/list_of_tz_database_time_zones.html
     ```
   - The `ignorelist.txt` file can be used for filtering time zones and thus
     reducing the execution time. For that purpose the sample file must be copied \
     `$ cp ignorelist.txt.sample ignorelist.txt` \
     and the countries, continents or regions that should be ignored must be
     inserted as new lines.
3. Generate a list of timezones to include, based on major cities and timezones included in Android:  
   `$ python utils/compile_whitelist.py`
4. Generate `zones.h` and `zones.c`:
   ```bash
   $ python utils/generate_zones.py -d vendor/tzdata -r africa -r asia -r australasia -r backward -r europe -r northamerica -r pacificnew -r southamerica -w whitelist.txt -i majorcities
   ```

Include different regions in step 5 based on your preferences.
(Modify the whitelist accordingly, then rerun step 4.)

### Examples

Build and run the example(s):

```bash
(venv) $ make examples
gcc -c -o utz.o utz.c -I.
gcc -c -o zones.o zones.c -I.
gcc -c -o examples/example.o examples/example.c -I.
examples/example.c: In function ‘main’:
examples/example.c:13:35: warning: format ‘%d’ expects argument of type ‘int’, but argument 2 has type ‘long unsigned int’ [-Wformat=]
   13 |   printf("Total library db size: %d B\n", sizeof(zone_rules) + sizeof(zone_abrevs) + sizeof(zone_defns) + sizeof(zone_names));
      |                                  ~^       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |                                   |       |
      |                                   int     long unsigned int
      |                                  %ld
gcc -o example utz.o zones.o examples/example.o -I.

(venv) $ ./example
Total library db size: 1727 B
San Francisco, current offset: -8.0
PST
```

Sidenote: The compiler warning only occurs on systems where the return value of sizeof is a
`long unsigned int`. It does not occur on embedded systems where sizeof returns a smaller integer.
