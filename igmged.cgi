#!/usr/bin/perl
#
# igmged, 14 Dec 1996, by Randy Winch <gumby@edge.net>
#
#############################################################################
#
# Produce GEDCOM subsets from the GED file
# Version 1.2
#
# 15 Sep 1997 Updated GEDCOM header handling
#############################################################################
$Program='IGMGed';
$Version='1.2';
require 'igmini';
require 'igmlib';
#
# Load variables passed each time program is called
# 
&LoadVars;
$DB=$FORM{'Database'};
$MaxLevel=$FORM{'Max'};
$MaxLevel=$MaxGED if ($MaxLevel>$MaxGED);
$key=$FORM{'Subject'};
$Name=$FORM{'Name'};
$Eol=$FORM{'Eol'};
$Type=$FORM{'type'};
$DB='GroatFamily';
#
# Set defaults and handle type if passed to routine
#
if ($Type eq 'descendants') {
  $t1='descendants';
  $t2='ancestors';
} else {
  $t1='ancestors';
  $t2='descendants';
}
$Email=$FORM{'Email'};
if (($MaxLevel eq '') || (!($Email=~/.*@.*/))) {
  &HTMLStart;
  &IGMHeader;
  print "<B><CENTER>GEDCOM Download</CENTER></B><HR>\n";
  print "<A HREF=\"http://www.cs.unm.edu/~mgroat/genealogy/GroatFamily/GroatFamily.ged\">Download full GEDCOM as a ZIP file</A><BR>\n";
  print "<P><FORM METHOD=\"POST\" ACTION=\"$WebCGIDir/$GedScript/$DB.ged\">\n";
  print "<INPUT TYPE=\"HIDDEN\" NAME=\"Database\" VALUE=\"$DB\">\n";
  print "<INPUT TYPE=\"HIDDEN\" NAME=\"Subject\" VALUE=\"$key\">\n";
  print "<INPUT TYPE=\"HIDDEN\" NAME=\"Name\" VALUE=\"$Name\">\n";
  print "<pre>\n";
  print "GEDCOM starting from:       $Name\n";
  print "Your Email Address:         ";
  print "<INPUT TYPE=\"TEXT\" NAME=\"Email\" SIZE=\"20\"> yourname\@yourdomain &nbsp;&nbsp;&nbsp; (You must put in an email address or the script will not work)\n";
  print "Produce a GEDCOM file from: ";
  print "<SELECT NAME=\"type\"><OPTION>$t1<OPTION>$t2</SELECT>\n";
  print "Number of generations:      ";
  print "<INPUT TYPE=\"TEXT\" NAME=\"Max\" VALUE=\"5\" SIZE=\"2\"> (Maximum of $MaxGED)\n";
  print "End of line character:      ";
  print "<SELECT NAME=\"Eol\"><OPTION>CRLF<OPTION>LF<OPTION>CR<OPTION>LFCR</SELECT>\n\n";
  print "</pre>\n";
  print "<INPUT TYPE=\"submit\" VALUE=\"Build GEDCOM\">\n";
  print "</FORM>\n<P>\n";
  print "<A HREF=\"$WebSite/$WebIGMDir/$DB/$DB.html\">Return to the master $NewTitle index.</A><BR><P>\n";
  open (DOWN,"downloads.dat") || die "Problem opening download counter: $!";
  $date = <DOWN>;
  $count = <DOWN>;
  close(DOWN);
  print "<HR><CENTER>There have been <H2>$count</H2> downloads since $date</CENTER>\n";

  &counter;
  &IGMRKW;
  exit 0;
} else {
  $starttime=(times)[0];
#
# Get Name and email information, correct single @ for GEDCOM
#
  open(DOWNLOADS,"downloads.dat") || die "Problem opening download counter: $!";
  my $date = <DOWNLOADS>;
  my $count = <DOWNLOADS>;
  $count++;
  close(DOWNLOADS);
  open(DOWNLOADS,">downloads.dat") || die "Problem opeing downloads counter: $!";
  print DOWNLOADS "$date";
  print DOWNLOADS "$count";
  close(DOWNLOADS);




  &IGMEmail;
  $emailaddr=~s/@/@@/;
#
# Set EOL variable
#
  if ($Eol eq 'CRLF') {
    $Eol="\r\n";
  } elsif ($Eol eq 'LF') {
    $Eol="\n";
  } elsif ($Eol eq 'CR') {
    $Eol="\r";
  } else {
    $Eol="\n\r";
  }
  $focus=$key;
#
# Read index file or open DBM file
#
  if ($UseDBM) {
    dbmopen(%idx,"$LocIGMDir/$DB/$DB",undef);
  } else {
    open(INDEX,"/nfs/notrust/cgi-bin/mgroat/$DB.idx") || die "Can't open index";
    while (<INDEX>) {
      /^(\S+) (.*)/;
      $idx{$1}=$2;
    }
    close(INDEX);
  }
  print "Content-Type: application/binary\n\n";
  open(GEDCOM,"/nfs/notrust/cgi-bin/mgroat/$DB.ged") || die "Can't open GEDCOM";
#
# Write gedcom header info
#
  $submitter='';
  $_=<GEDCOM>;
  chop;
  print "$_$Eol";
  while (<GEDCOM>) {
    ($lvl,$tag,$rest)=/^(\d+)\s+(\S+) ?(.*)$/o;
    last if ($lvl eq '0');
    chop;
    print "$_$Eol";
    if ($tag eq 'SUBM') {
      ($submitter)=($rest=~/^\@(.*)\@$/);
    }
  }
#
# Output Submitter info 
#
  if ($submitter) {
    $seek=$idx{$submitter};
    if ($seek) {
      seek(GEDCOM,$seek,0);
      $_=<GEDCOM>;
      chop;
      print "$_$Eol";
      while (<GEDCOM>) {
        ($lvl,$tag,$rest)=/^(\d+)\s+(\S+) ?(.*)$/o;
        last if ($lvl eq '0');
        chop;
        print "$_$Eol";
      }
    }
  }
      
  $seek=$key;
  $seek=$idx{$key} if ($UseXrefTags);
  seek(GEDCOM,$seek,0);
#
# Get the list of individuals to include
#
  if ($Type eq 'descendants') {
    &Descendents($key);
  } else {
    &Ancestors($key);
  }
  foreach $person (@people) {
    $Individuals{$person}='y';
    &GetIndividuals($person);
  }
#
# Dump individual data, record non-individual xref tags
#
  foreach $person (sort keys(%Individuals)) {
    $seek=$idx{$person};
    seek(GEDCOM,$seek,0) || die "Can't seek to $key";
    $_=<GEDCOM>;
    chop;
    print "$_$Eol";
    while (<GEDCOM>) {
      ($lvl,$tag,$rest)=/^(\d+)\s+(\S+) ?(.*)$/o;
      last if ($lvl eq '0');
      chop;
      print "$_$Eol";
      $Xrefs{$1}='y' if ($rest=~/^\@(.*)\@$/);
    }
#
# Add a note to remind user where the data came from
#
    print "1 NOTE Provided by: $emailname <$emailaddr>$Eol";
  }
#
# Now output any other referenced section (notes, sources, family)
#
  foreach $person (sort keys(%Xrefs)) {
    $seek=$idx{$person};
    seek(GEDCOM,$seek,0) || die "Can't seek to $key";
    $_=<GEDCOM>;
    chop;
    print "$_$Eol";
    while (<GEDCOM>) {
      ($lvl,$tag,$rest)=/^(\d+)\s+(\S+) ?(.*)$/o;
      last if ($lvl eq '0');
      chop;
#
# If an Xref tag then it must be to a previously included individual
#
      if ($rest=~/^\@(.*)\@$/) {
        print "$_$Eol" if ($Individuals{$1});
      } else {
        print "$_$Eol";
      }
    }
  }
  print "0 TRLR$Eol";
  $time=(times)[0]-$starttime;
  &IGMLog("GEDCOM of $Type, $MaxLevel generations from $Name accessed by $ENV{\"REMOTE_HOST\"} $Email using $time");
  exit 0;
}
#
# Subroutine to return a list of people in a descendency tree
#
sub Descendents {
  ($key)=@_;
  local ($oldseek)=tell;
  $key=$1 if ($key=~/@(\S+)@/o);
  $seek=$idx{$key};
  seek(GEDCOM,$seek,0) || die "Can't seek to $key";
  $_=<GEDCOM>;
  ($lvl,$tag,$rest)=/^(\d+)\s+(\S+) ?(.*)$/o;
#
# Record individuals
#
  if ($rest eq 'INDI') {
    ($tag)=($tag=~/@(.*)@/);
    push(@people,$tag) if ($tag);
  }
  while (<GEDCOM>) {
    ($lvl,$tag,$rest)=/^(\d+)\s+(\S+) ?(.*)$/o;
    last if ($lvl eq '0');
    if ($tag eq 'FAMS') {
      &Descendents($rest);
      next;
    }
    if ($tag eq 'CHIL') {
      if ($Level<$MaxLevel) {
        $Level++;
        &Descendents($rest);
        $Level--;
      }
    }
  }
  seek(GEDCOM,$oldseek,0) || die "Can't seek to $oldseek";
}
#
# Subroutine to return a list of people in a ancestor tree
#
sub Ancestors {
  ($key)=@_;
  local ($oldseek)=tell;
  $key=$1 if ($key=~/@(.*)@/o);
  $seek=$idx{$key};
  seek(GEDCOM,$seek,0) || die "Can't seek to $key";
  $_=<GEDCOM>;
  ($lvl,$tag,$rest)=/^(\d+)\s+(\S+) ?(.*)$/o;
#
# Record individuals
#
  if ($rest eq 'INDI') {
    ($tag)=($tag=~/@(.*)@/);
    push(@people,$tag) if ($tag);
  }
  while (<GEDCOM>) {
    ($lvl,$tag,$rest)=/^(\d+)\s+(\S+) ?(.*)$/o;
    last if ($lvl eq '0');
    if ($tag eq 'FAMC') {
      &Ancestors($rest);
      next;
    }
    if (($tag eq 'HUSB') || ($tag eq 'WIFE')) {
      if ($Level<$MaxLevel) {
        $Level++;
        &Ancestors($rest);
        $Level--;
      }
    }
  }
  seek(GEDCOM,$oldseek,0) || die "Can't seek to $oldseek";
}
#
# Subroutine to return a list of referenced people in a family
#
sub GetIndividuals {
  ($key)=@_;
  local ($oldseek)=tell;
  $key=$1 if ($key=~/@(.*)@/o);
  $seek=$idx{$key};
  seek(GEDCOM,$seek,0) || die "Can't seek to $key";
  <GEDCOM>;
  while (<GEDCOM>) {
    &IGMGetLine;
    last if ($lvl eq '0');
    if ($tag eq 'FAMS') {
      &GetIndividuals($rest);
      next;
    }
    if (($tag eq 'HUSB') || ($tag eq 'WIFE') || ($tag eq 'CHIL')) {
      ($key)=($rest=~/@(.*)@/);
      $Individuals{$key}='y';
    }
  }
  seek(GEDCOM,$oldseek,0) || die "Can't seek to $oldseek";
}
