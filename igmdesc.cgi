#!/usr/bin/perl
#
# igmdesc, 1 Nov 1996, by Randy Winch <gumby@edge.net>
#
#############################################################################
#
# Version 1.2
#
#############################################################################
sub trim($);
$Program = 'IGMDesc';
$Version = '1.2';
require 'igmini';
require 'igmlib';
#
# Get database name
#
$starttime=(times)[0];
$tmp=$ENV{'PATH_INFO'};
#(($DB)=($tmp =~ m#^/n=(.*)#)) || &IGMDie("PATH_INFO \"$tmp\" not in correct format.");
#
$DB='GroatFamily';
# Get starting seek address
#
$tmp=$ENV{'QUERY_STRING'};
(($key)=($tmp =~ /(\w+)/)) || &IGMDie("QUERY_STRING \"$tmp\" not in correct format.");
$focus=$key;
#
# Read in Index or open DBM file
#
if ($UseDBM) {
  dbmopen(%idx,"$LocIGMDir/$DB/$DB",undef);
} else {
  open(INDEX,"/nfs/notrust/cgi-bin/mgroat/GroatFamily.idx") || &IGMDie("Can't open index");
  while (<INDEX>) {
    /^(\S+) (.*)/;
    $idx{$1}=$2;
  }
  close(INDEX);
}
#
# Translate xref tag to seek address if needed
#
$key=$idx{$key} if ($UseXrefTags);
$lastlvl = 100;
open(GEDCOM,"/nfs/notrust/cgi-bin/mgroat/GroatFamily.ged") || &IGMDie("Can't open GEDCOM");
seek(GEDCOM,$key,0);
#
# Read INDI line and get tag for comparison later
#
$_=<GEDCOM>;
($subject)=/^\d+\s+(\S+)\s+.*$/;
#
# Set maximum number of levels to recurse
#
$MaxLevel=$Descdepth-1;
$Level=0;
$start=1;
&HTMLStart;
&IGMHTMLHeader;
&DoParent($subject);
print "</pre><br>";
#
# URL Encode $Savename
#
$EncodeName=&escape($Savename);

print "<HR><CENTER><B><A HREF=\"$WebSite/$WebIGMDir/$DB/$DB.html\">Master Index</A>\n";
print " | <A HREF=$WebCGIDir/igmget.cgi/n=$DB?$focus>Individual</A>\n";
print " | <A HREF=$WebCGIDir/$PedScript/n=$DB?$focus>Pedigree Chart</A>\n";

#
# If GEDCOM extraction is allowed the show them and allow additions
#
if ($AllowGED) {
  print " | <a href=$WebCGIDir/$GedScript?Database=$DB&Subject=$focus&Name=$EncodeName&type=descendants>Extract GEDCOM</a></B></CENTER>\n";
#  print "<FORM METHOD=\"POST\" ACTION=\"$WebCGIDir/$GedScript\">\n";
#  print "<INPUT TYPE=\"HIDDEN\" NAME=\"Database\" VALUE=\"$DB\">\n";
#  print "<INPUT TYPE=\"HIDDEN\" NAME=\"Subject\" VALUE=\"$focus\">\n";
#  print "<INPUT TYPE=\"HIDDEN\" NAME=\"Name\" VALUE=\"$Savename\">\n";
#  print "<INPUT TYPE=\"HIDDEN\" NAME=\"type\" VALUE=\"descendants\">\n";
#  print "<INPUT TYPE=\"submit\" VALUE=\"Extract GEDCOM\">\n";
#  print "</FORM>\n";
}

#print "<br><A HREF=\"$WebSite/$WebIGMDir/$DB/";
#print "$DB.html\">Return to the master $NewTitle index.</A><BR>\n";
#print "<A HREF=$WebSite/$WebCGIDir/$PedScript/n=$DB?$focus>Pedigree Chart</A><BR>\n";
&counter;
&IGMRKW;
dbmclose(%idx) if ($UseDBM);
$time=(times)[0]-$starttime;
&IGMLog("Descendency $Savename accessed by $ENV{\"REMOTE_ADDR\"} $ENV{\"HTTP_USER_AGENT\"} using $time");
#
# Subroutine to print name and birthdate
#

$array_size = 14000;

@appeared_or_not = (0) x $array_size;

sub DoParent {
  local ($subject)=@_;
  local ($oldseek)=tell;
#  local ($tag,$type,$rest)=('','','');
  ($key)=($subject=~/@(\S+)@/o);
  local $tempkey = substr $key, 1;
  local $temptempkey = $key;
  local $indiv_or_not = substr $key, 0, 1;
#  print "XXX $indiv_or_not ";
  $seek=$idx{$key};
  $key=$seek unless ($UseXrefTags);
  seek(GEDCOM,$seek,0) || die "Can't seek to $key";
  $type='';
  <GEDCOM>;
  while (<GEDCOM>) {
    &IGMGetLine;
    last if ($lvl eq '0');
    $type = $tag if ($lvl eq '1');
    if ($tag eq 'NAME') {
      $rest=~s|/| |g;
      $rest=~s/\s{2,}/ /g;
      $rest=~s/ ,/,/g;
      $rest = trim($rest);
      if ($Level==0) {
        print "<h1>Descendents of $rest</h1>";

        print "<HR><CENTER><B><A HREF=\"$WebSite/$WebIGMDir/$DB/$DB.html\">Master Index</A>\n";
        print " | <A HREF=$WebCGIDir/igmget.cgi/n=$DB?$focus>Individual</A>\n";
        print " | <A HREF=$WebCGIDir/$PedScript/n=$DB?$focus>Pedigree Chart</A>\n";


        if ($AllowGED) {
          print " | <a href=$WebCGIDir/$GedScript?Database=$DB&Subject=$focus&Name=$EncodeName&type=descendants>Extract GEDCOM</a></B></CENTER><HR><pre>\n";
        }
        $Savename=$rest;
      }
      print "\n",' ' x ($Level*4),($Level+1);
      
      if(@appeared_or_not[$tempkey] == 0){
         print " <A HREF=$WebCGIDir/$GetScript/n=$DB?$key>$rest</A>";
         print "<A NAME=\"$temptempkey\"></A>";
      } else {
         print " <A HREF=$WebCGIDir/$GetScript/n=$DB?$key>$rest</A>";
         print " <A HREF=\"#$temptempkey\">(Person is repeated. Click for first appearance.)</A> ";
      }
      next;
    }
    if ($tag eq 'DATE') {
      $rest = trim($rest);
      print " b $rest" if ($type eq 'BIRT');
      print " d $rest" if ($type eq 'DEAT');
      next;
    }
    if ($tag eq 'FAMS') {
      $savesubject=$subject;
#      print " YYY $indiv_or_not ";
      &DoParent($rest) if (@appeared_or_not[$tempkey] == 0);
      next;
    }
    if ($tag eq 'CHIL') {
      if ($Level<$MaxLevel) {
        $Level++;
#        print " XXX $indiv_or_not ";
        &DoParent($rest) if(@appeard_or_not[$tempkey] == 0);
        $Level--;
      }
    }
    #print "AA" . $rest . "AA";
    #print "BB" . $savesubject . "BB";

    $tmprest = trim($rest);
    $tmpsavesubject = trim($savesubject);
    if (($tag eq 'WIFE') && ($tmprest ne $tmpsavesubject)) {
      &Doname($rest) if ($Level<$MaxLevel);
      next;
    }
    if (($tag eq 'HUSB') && ($tmprest ne $tmpsavesubject)) {
      &Doname($rest) if ($Level<$MaxLevel);
      next;
    }
    $type=$tag if ($rest eq '');
  }
  if ($indiv_or_not eq "I") {
    @appeared_or_not[$tempkey] = 1;
  }
  seek(GEDCOM,$oldseek,0) || die "Can't seek to $oldseek";
}
#
# Subroutine to print name and birthdate
#
sub Doname {
  local ($key)=@_;
  local ($oldseek)=tell;
#  local ($type,$lvl,$tag,$rest)=('','','','');
  ($key)=($key=~/@(\S+)@/o);
  $seek=$idx{$key};
  $key=$seek unless ($UseXrefTags);
  seek(GEDCOM,$seek,0) || die "Can't seek to $key";
  <GEDCOM>;
  while (<GEDCOM>) {
    &IGMGetLine;
    last if ($lvl eq '0');
    $type = $tag if($lvl eq '1');
    if ($tag eq 'NAME') {
      $rest=~s|/||g;
      print "\n",' ' x ($Level*4);
      $rest = trim($rest);
      print "  + <A HREF=$WebCGIDir/$GetScript/n=$DB?$key>$rest</A>";
    } elsif ($tag eq 'DATE') {
      $rest = trim($rest);
      print " b. $rest" if ($type eq 'BIRT');
      print " d. $rest" if ($type eq 'DEAT');
    }
    $type=$tag if ($rest eq '');
  }
  seek(GEDCOM,$oldseek,0) || die "Can't seek to $oldseek";
}

sub trim($){
   my $string = shift;
   $string =~ s/^\s+//;
   $string =~ s/\s+$//;
   return $string;
}
