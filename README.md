# Usenet mbox tools

Tools for working with Usenet archives in mbox format

## Quickstart (example)

Grab list of files in the [SFnet archive](https://archive.org/download/usenet-sfnet)

```
export BASEURL=https://archive.org/download/usenet-sfnet

curl $BASEURL \
    | egrep '<a [^<>]*href="sfnet[^"]*\.mbox\.zip' \
    | perl -pe 's/.*?<a [^<>]*href="(sfnet[^"]*\.mbox\.zip)".*/$1/' \
    > files.txt
```

Download and unpack the first 5 files

```
head -n 5 files.txt | while read f; do wget -nc $BASEURL/$f; done
for f in *.zip; do unzip $f; done
```

Get text content

```
for f in *.mbox; do python ../get_mbox_content.py $f > ${f%.mbox}.txt; done
```
