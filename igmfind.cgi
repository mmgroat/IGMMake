#!/usr/bin/perl
#
# igmfind, 16 Apr 1996, by Tim Doyle <tdoyle@doit.com>
#
#############################################################################
# - Change Log -
# Version 2.0  Fixed background on initial screen
#              Fixed bug which would halt script (with no hits listed)
#                if EOF was reached in search
#              Added support for ID style indexing
#              Changed headings
#              Names of matched individuals now print properly
# Version 2.1  Added Program & Version variables
#              Implemented IGM.PL library
#              Reorganized code
#              Enhanced Find screen layouts
#              Added igm.ini file - SL
# Version 2.2  Added ability to search for multiple terms - BB
#              Added case sensitivity, boolean operators, Max hits - BB
#              Changed double quotes to single where appropriate
#              Fixed seek address problems
#              Matched names now print in last, first order
#              Matched names now sort properly
#              Default boolean to OR (easier on program)
#              Multiple search terms now properly works even if terms
#                are on different lines in the GEDCOM file
#              Renamed igm.ini to igmini
#              Renamed igm.pl to igmlib
#              Searches are now logged to the log file
#              Blank tags no longer abort search
# Version 2.2a Location variables modified - HM
#              Set MaxMatches from user selection
#              Added directory for required files - BB
# Version 2.3  No changes
#
# Still To Do: Need to implement date ranges as in IGMMake
#              Add places for people
#              Correctly handle special characters in terms
#              Search not working for BB & SL
#############################################################################

use Cwd qw( abs_path );
use File::Basename qw( dirname );
use lib dirname(abs_path($0));
sub trim($);
$starttime=(times)[0];
$Program = 'IGMFind';
$Version='2.3';
require 'igmini';
require 'igmlib';
$|=1;

&LoadVars;
$tmp=$ENV{'PATH_INFO'};
($DB)=($tmp=~m#^/n=(.*)#);
$DB='GroatFamily';
if (!($FORM{'terms'})) {
  &HTMLStart;
  &IGMHeader('Search Engine');
  print "<P><FORM METHOD=\"POST\" ACTION=\"$FindScript\">\n";
  print "<INPUT TYPE=\"HIDDEN\" NAME=\"Database\" VALUE=\"$DB\">\n";
  print "Enter word(s) to search for below with a space between each word.\n<br>";
#  print "<FONT SIZE=+3>Search for:</FONT> ";
  print "<INPUT TYPE=\"TEXT\" NAME=\"terms\" SIZE=\"50\">\n<BR><BR>";
  print "If searching for multiple words, use boolean: \n";
  print "<SELECT NAME=\"boolean\"><OPTION>OR<OPTION>AND</SELECT>\n<P>\n";
  print "The search should be case: \n";
  print "<SELECT NAME=\"case\"><OPTION>insensitive<OPTION>sensitive";
  print "</SELECT>\n<P>\n";
  print "Maximum Hits: ";
  print "<SELECT NAME=\"MaxHits\"><OPTION>100<OPTION>200<OPTION>500<OPTION>1000\n";
  print "</SELECT>\n<P>\n";
  print "<INPUT TYPE=\"submit\" VALUE=\"Begin Search\">\n";
  print "</FORM>\n<P>\n";
  print "<A HREF=\"$WebSite/$WebIGMDir/$DB/$DB.html\">";
  print "Return to the master $DB index.</A><BR><P>\n";
  &IGMEnd;
  exit 0;
} else {
  $starttime=(times)[0];
  &HTMLStart;
  $DB = $FORM{ 'Database' };
  $MaxMatches = $FORM{ 'MaxHits' };
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
  &IGMHeader( 'Search Results' );
  print "The $DB genealogical Database is now being searched for \n";
  @terms = split( /\s+/, $FORM{ 'terms' } );
  $i = 0;
  $FindThis = "<B>";
  foreach $term ( @terms ) {
    $FindThis .= "$term";
    $i++;
    if ( ! ( $i == @terms ) ) { $FindThis .= " $FORM{ 'boolean' } "; }
  }
  $FindThis .= "</B>";
  print "$FindThis";
  print "</B><P>The search will be case $FORM{ 'case' }.\n";
  print "<P>\nPlease wait...<BR>\n";
  $Pf = "/nfs/notrust/cgi-bin/mgroat/$DB.ged";
  open( GEDCOM, $Pf ) || &IGMDie( "Error opening $Pf." );
  $MatchCount = 0;
  $MatchCount = &Srch( @terms );
  close ( GEDCOM );

  if ( $MatchCount == 0 ) {
    print "<HR>Search complete. There are no matches.<P>\n";
    print "<A HREF=\"$WebSite/$WebIGMDir/$DB/$DB.html\">";
    print "Return to the master $DB index.</A><BR>\n";
    print "<A HREF=\"$FindScript/n=$DB\">";
    print "Perform another search.</A><BR><P>\n";
  } else {
    print "<HR>Search complete. Matches were found in the records\n";
    print "for the following individuals:";
    print "<UL>";
    foreach $Name ( sort { &IGMConvert2($a) cmp &IGMConvert2($b) } keys( %Match ) ) {
      ( $Seek ) = $Match{ $Name };
      ( $PrintName ) = $Name =~ /(.*):\d+/o;
      $PrintName =~ s|/| <b>|o;
      $PrintName =~ s|/|</b> |o;
      $PrintName =~ s|_| |o;
      $PrintName =~ s|\s+| |o;
      print "<LI><A HREF=$WebCGIDir/$GetScript/n=$DB?$Seek>";
      print "$PrintName</A>$Dates\n";
    }
    print "</UL>\n";
    if ( $MatchCount >= $MaxMatches ) {
      print "The maximum match count of $MaxMatches was reached.\n";
      print "Perhaps you need to make your search more restrictive.<P>\n";
    }
    print "<A HREF=\"$WebSite/$WebIGMDir/$DB/$DB.html\">";
    print "Return to the master $DB index.</A><BR>\n";
    print "<A HREF=\"$FindScript/n=$DB\">";
    print "Perform another search.</A><BR><P>\n";
  }
  &IGMEnd();
  $time=(times)[0]-$starttime;
  &IGMLog("Database searched for string $FindThis by $ENV{\"REMOTE_HOST\"} using $time");
}

sub Srch {
  seek(GEDCOM,0,0);
  $seek=tell;
  while (<GEDCOM>) {
    &IGMGetLine;
    next if ($tag eq '');
    if ($lvl eq '0') {
      &IGMGetKey;
      $CurrentKey=$key;
      $Pointer='';
      if ($rest eq 'INDI') {
        if ($UseXrefTags) {
          ($CurrentSeek)=($tag=~/@(.*)@/);
        } else {
          $CurrentSeek=$seek;
        }
        $MatchCounter=0;
        $Matched=();
#        foreach $key (keys %Matched) {delete $Matched{$key};}
      }
    }
    if ($tag eq 'NAME') {
      ($firstname,$lastname,$title)=($rest=~m#(.*)/(.*)/,*\s*(.*)#o);
      $CurrentName="$lastname, $firstname $title";
      $Pointer=$CurrentSeek if ($Pointer eq '');
    } elsif ($tag eq 'NUMB') {
      $rest=~s/\s//go;
      $Pointer="ID$rest";
      next;
    }
    next if ($LastMatchKey eq $Pointer);

    @_ = $rest;
    s/\r\n$//go;

    $Matched=0;
    $TermCount=@terms;
    foreach $term (@terms) {
      $m=$Case?/$term/:/$term/i;
      if ($m) {
        if ($Boolean) {
          $Matched=1;
          last;
        } else {
          if ($Matched{$term}!=1) {
            $Matched{$term}=1;
            $MatchCounter++;
          }
          if ($MatchCounter==$TermCount) {
            $Matched=1;
            last;
          }
        }
      }
    }
    if ($Matched) {
      $LastMatchKey=$Pointer;
      if ($CurrentKey=~/^I/) {
        $MatchCount++;
        $Match{ "$CurrentName:$MatchCount" } = "$Pointer";
#       Bug in this routine  } else { &Srch( $CurrentKey );
      }
    }
    last if ($MatchCount==$MaxMatches);
    $seek=tell;
  }
  $MatchCount;
}
