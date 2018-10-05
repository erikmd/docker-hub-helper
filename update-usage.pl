#!/usr/bin/env perl
# -*- coding: utf-8 -*-
# Copyright (c) 2018  Érik Martin-Dorel
# Licensed under BSD-3 <https://opensource.org/licenses/BSD-3-Clause>
use strict;
use warnings;
use File::Basename;
my $dirname = dirname(__FILE__);
my $f_md = "$dirname/README.md";
open(my $fd_md, '<', $f_md);
my $f_new = "$f_md.new";
open(my $fd_new, '>', $f_new);
my $step = 0;

while (<$fd_md>) {
    if (m/^```/) {
        print $fd_new $_;
        if ($step == 0) { # first block detected
            open(my $fd_dhh, '-|', "$dirname/dhh", '-h');
            while (<$fd_dhh>) {
                print $fd_new $_;
            }
            close $fd_dhh;
            $step++;
        } elsif ($step == 1) { # end of first block
            $step++;
        }
    } else {
        print $fd_new $_ if $step != 1; # skip contents of first block
    }
}

close $fd_md;
close $fd_new;
my @cp = ('mv', '-f', '-v', '--', $f_new, $f_md);
system(@cp);
