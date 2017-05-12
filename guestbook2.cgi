#!/usr/bin/perl

use strict;
use warnings;

my $filename = 'guestbook.html';
open (my $fh, '<:encoding(UTF-8)', $filename)
   or die "Could not open file";
while (my $row = <$fh>) {
   chomp $row;
   print "$row\n";
}

