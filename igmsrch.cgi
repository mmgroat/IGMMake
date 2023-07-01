#!/usr/bin/perl
#
# igmsrch, 14 Nov 1996, by Randy Winch <gumby@edge.net>
#
#############################################################################
#
# Search the gdx file for strings instead of the GED file
# Version 1.0
#
#############################################################################

use Cwd qw( abs_path );
use File::Basename qw( dirname );
use lib dirname(abs_path($0));
sub trim($);
$starttime=(times)[0];
$Program='IGMSrch';
$Version='1.0';
require 'igmini';
require 'igmlib';
&LoadVars;
$tmp=$ENV{'PATH_INFO'};
#($DB)=($tmp=~m#^/n=(.*)#);
$DB='GroatFamily';
if (!($FORM{'terms'})) {
  &HTMLStart;
  &IGMHeader( 'Search Engine' );
  print "<P><FORM METHOD=\"POST\" ACTION=\"$WebCGIDir/$SrchScript\">\n";
  print "<INPUT TYPE=\"HIDDEN\" NAME=\"Database\" VALUE=\"$DB\">\n";
  print "Enter word(s) to search for below with a space between each word.\n<br>";
#  print "<FONT SIZE=+3>Search for:</FONT> ";
  print "<INPUT TYPE=\"TEXT\" NAME=\"terms\" SIZE=\"50\">\n<BR><BR>";
  print "If searching for multiple words, use boolean: \n";
  print "<SELECT NAME=\"boolean\"><OPTION>AND<OPTION>OR</SELECT>\n<P>\n";
  print "The search should be case: \n";
  print "<SELECT NAME=\"case\"><OPTION>insensitive<OPTION>sensitive";
  print "</SELECT>\n<P>\n";
  print "Maximum Hits: ";
  print "<SELECT NAME=\"MaxHits\"><OPTION>100<OPTION>200<OPTION>500<OPTION>1000\n";
  print "</SELECT>\n<P>\n";
  print "<INPUT TYPE=\"submit\" VALUE=\"Begin Search\">\n";
  print "</FORM>\n<P>\n";
  print "<A HREF=\"$WebSite/$WebIGMDir/$DB/$DB.html\">Return to the master $NewTitle index.</A><BR><P>\n";
  &IGMRKW;
  exit 0;
} else {
  $starttime=(times)[0];
  &HTMLStart;
  $DB=$FORM{'Database'};
  $DB='GroatFamily';
  $MaxMatches=$FORM{'MaxHits'};
#
# Set a true/false variable so we don't eval this all of the time
#
  if ($FORM{'case'} eq 'sensitive') {
    $Case=1;
  } else {
    $Case=0;
  }
  if ($FORM{'boolean'} eq 'OR') {
    $Boolean=1;
  } else {
    $Boolean=0;
  }
  &IGMHeader('Search Results');
  print "The $NewTitle genealogical Database is now being searched for \n";
#
# Remove any improper characters from search string and split into words
#
  $term=$FORM{'terms'};
  $term=~tr/,\\\///d;
  @terms=split(/\s+/,$term);
  $i=0;
  $FindThis='<B>';
  foreach $term (@terms) {
    $FindThis.="$term";
    $i++;
    $FindThis.=" $FORM{'boolean'} " unless ($i==@terms);
  }
  $FindThis.='</B>';
  print "$FindThis";
  print "</B><P>The search will be case $FORM{'case'}.\n";
  open(GEDCOM,$LocGDX) || &IGMDie( "Error opening $LocGDX" );
  $MatchCount=0;
  $MatchCount=&Srch(@terms);
  close (GEDCOM);

  if ($MatchCount==0) {
    print "<HR>Search complete. There are no matches.<P>\n";
  } else {
    print "</UL>\n";
    if ( $MatchCount >= $MaxMatches ) {
      print "The maximum match count of $MaxMatches was reached.\n";
      print "Perhaps you need to make your search more restrictive.<P>\n";
    }
  }
  print "<A HREF=\"$WebSite/$WebIGMDir/$DB/$DB.html\">Return to the master $NewTitle index.</A><BR>\n";
  print "<A HREF=\"$SrchScript/n=$DB\">Perform another search.</A><BR><P>\n";
  &IGMRKW;
  $time=(times)[0]-$starttime;
  &IGMLog("Database searched for name $FindThis by $ENV{\"REMOTE_HOST\"} using $time");
}
#
# Subroutine to do the actual searching
#
sub Srch {
  seek(GEDCOM,0,0);
  while (<GEDCOM>) {
#    study;
    foreach $term (@terms) {
      $Matched=$Case?/$term/:/$term/i;
      last if ($Boolean?$Matched:!$Matched);
    }
    if ($Matched) {
      ($seek,$surname,$name,$birthdate,$birthplace,$deathdate,$deathplace)=split(/\|/,$_);
      ($firstname,$lastname,$title)=$name=~m#(.*)/(.*)/,*\s*(.*)#o;
      $PrintName="$lastname, $firstname $title";
      if ($MatchCount==0) {
        print "<HR>Search complete. Matches were found in the records ";
        print "for the following individuals:";
        print "<UL>";
      }
      $MatchCount++;
      $PrintName=~s|/| <b>|o;
      $PrintName=~s|/|</b> |o;
      $PrintName=~s|_| |o;
      $PrintName=~s|\s+| |o;
      print "<LI><A HREF=$WebCGIDir/$GetScript/n=$DB?$seek>$PrintName</A> b. $birthdate $birthplace d. $deathdate $deathplace\n";
    }
    last if ($MatchCount==$MaxMatches);
  }
  return $MatchCount;
}
