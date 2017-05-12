#!/usr/bin/perl
#
# igmget, 16 Apr 1996, by Tim Doyle <tdoyle@doit.com>
#                      by Randy Winch <gumby@edge.net>
#
#############################################################################
#
# This program provides for on-the-fly individual page generation
#
# 02 Feb 1998 Revised Family handling and added photo support
# 16 Sep 1997 Changed format of pedigree, descendency, etc., links
#             Also added support for $HomePage link
# 15 Sep 1997 Updated source handling & added achema handling
#             Added note handling for marriages
#############################################################################
# Some systems might need to uncomment the following line
#$|=1;
sub trim($);
$starttime=(times)[0];
$Program='IGMGet (modified by Randy Winch)';
$Version='2.7';
require 'igmini';
require 'igmlib';
#$tmp=$ENV{'PATH_INFO'};
#(($DB)=($tmp=~m#^/n=(.*)#)) || &IGMDie("PATH_INFO \"$tmp\" not in correct format.");
$DB='GroatFamily';
$tmp=$ENV{'QUERY_STRING'};
#$tmp='986563';
(($key)=($tmp=~/(\w+)/)) || &IGMDie("QUERY_STRING \"$tmp\" not in correct format.");
#
$focus=$key;
#
# Read index file or open DBM file
#
if ($UseDBM) {
  dbmopen(%idx,"/nfs/notrust/cgi-bin/mgroat/GroatFamily",undef);
} else {
  open(INDEX,"/nfs/notrust/cgi-bin/mgroat/GroatFamily.idx") || die "Can't open index";
  while (<INDEX>) {
    /^(\S+) (.*)/;
    $idx{$1}=$2;
  }
  close(INDEX);
}
$key=$idx{$key} if ($UseXrefTags);

#

$lastlvl=100;
open(GEDCOM,"/nfs/notrust/cgi-bin/mgroat/GroatFamily.ged") || die "Can't open GEDCOM";
#
# Read schema from gedcom file
#

%famschema=();
%indischema=();
$lasttag='';
$indi='y';
$cnt=0;
<GEDCOM>;
while (<GEDCOM>) {
  ($lvl,$tag,$rest)=/^(\d+)\s+(\S+) ?(.*)$/o;
  last if ($lvl eq '0');
  if ($tag eq 'LABL') {
    if ($indi) {
      $indischema{$lasttag}=$rest;
    } else {
      $famschema{$lasttag}=$rest;
    }
  } elsif ($tag eq 'FAM') {
    $indi='';
  }
  $lasttag=$tag;
}
seek(GEDCOM,$key,0);
#
# Read INDI line and get tag for comparison later
#
$_=<GEDCOM>;
($subject)=/^\d+\s+(\S+)\s+.*$/;
&HTMLStart;
&IGMHTMLHeader;
$Savename='';
$SourceText='';
$GotSource='';
$lastlvl=0;
$tag='';
$SourceNo=0;

while (<GEDCOM>) {
  $lasttag=$tag;
  &IGMGetLine;
  if ($lvl <= $lastlvl) {
    if ($GotSource) {
      print &AddSource;
      $GotSource='';
      $SourceText='';
    }
    if ($req) {
      print "$req";
      $req='';
    }
    $lastlvl=0;
  }
  last if ($lvl eq '0');
  if ($tag eq 'NAME') {
    $rest=~s|/| |go;
    $rest=~s/\s{2,}/ /go;
    $rest=~s/ ,/,/go;
    print "<H1>$rest</H1><HR>\n<ul>";
    $Savename=$rest;
    next;
  }
  if ($tag eq 'SEX')  {print "\n<li><em>Sex:</em> $rest"; next;}
  if ($tag eq 'DATE') {print " $rest"; next;}
  if ($tag eq 'PLAC') {print " in $rest"; next;}
  if ($tag eq 'BIRT') {print "\n<li><em>Born:</em>"; next;}
  if ($tag eq 'DEAT') {print "\n<li><em>Died:</em>"; next;}
  if ($tag eq 'FAMC') {push(@Parents,$rest); next}
  if ($tag eq 'FAMS') {push(@Children,$rest); next}
  if ($tag eq 'SOUR') {
    print "\n<li><em>Source</em>" if ($lasttag eq 'NAME');
    $GotSource='y';
    $lastlvl=$lvl;
    if ($rest=~/@(\S+)@/o) {
      &DoNotes($rest);
    } else {
     $SourceText=$rest;
    }
    next;
  }
  if ($tag eq 'AFN')  {print "\n<li><em>AFN:</em> $rest"; next;}
  if ($tag eq 'ALIA') {
    $rest=~s|/||go;
    print "\n<li><em>Also Known As:</em> $rest";
    next;
  }
  next if ($tag eq 'ANCI');
  if ($tag eq 'ANEC') {print "<li>$rest"; next;}
  next if ($tag eq 'ATTR');
  if ($tag eq 'AUTH') {print " $rest"; next;}
  if ($tag eq 'BAPM') {print "\n<li><em>Baptized:</em> $rest"; next;}
  if ($tag eq 'BAPL') {print "\n<li><em>Baptised LDS: $rest"; next;}
  if ($tag eq 'BAPM') {print "\n<li><em>Baptised: $rest"; next;}
  if ($tag eq 'BLES') {print "\n<li><em>Blessing: $rest"; next;}
  if ($tag eq 'BURI') {print "\n<li><em>Buried:</em>"; next;}
  if ($tag eq 'CALN') {print " $rest"; next;}
  if ($tag eq 'CEME') {print "\n<li><em>Cemetery:</em> $rest"; next;}
  if ($tag eq 'CENS') {print "\n<li><em>Census:</em> $rest"; next;}
  if ($tag eq 'CHAN') {print "\n<li><em>Record last updated:</em> $rest"; next;}
  if ($tag eq 'CHR')  {print "\n<li><em>Christened:</em> $rest"; next;}
  if ($tag eq 'CONC') {
    if ($GotSource) {
      $SourceText.="$rest";
    } else {
      print "$rest";
    }
    next;
  }
  if ($tag eq 'CONF') {print "\n<li><em>Confirmed:</em> $rest"; next;}
  if ($tag eq 'CONT') {
    if ($GotSource) {
      $SourceText.="<br>\n$rest";
    } else {
      print "<br>\n$rest";
    }
    next;
  }
  if ($tag eq 'DIVF') {print "\n<li><em>Divorce Filed:</em> $rest "; next;}
  if ($tag eq 'EDUC') {print "\n<li><em>Educated:</em> $rest"; next;}
  if ($tag eq 'EMIG') {print "\n<li><em>Emigrated:</em> $rest"; next;}
  if ($tag eq 'EMPL') {print "\n<li><em>Employed:</em> $rest"; next;}
  if ($tag eq 'ENGA') {print "\n<li><em>Engaged:</em> $rest"; next;}
  next if ($tag eq 'EVEN');
  if ($tag eq 'FCOM') { print "<BR><B>1st Communion:</B> $rest"; next;}
  if ($tag eq 'FIDE') {next;}
  if ($tag eq 'FILM') {print "microfilm number $rest"; next;}
  if ($tag eq 'FREE') {print "\n<li><em>Made Freeman:</em> $rest"; next;}
  if ($tag eq 'FROM') {print "\n<li><em>From:</em> $rest"; next;}
  if ($tag eq 'FUNR') {print "\n<li><em>Funeral:</em> $rest"; next;}
  if ($tag eq 'HOBY') {print "\n<li><em>Hobby:</em> $rest"; next;}
  if ($tag eq 'GRAD') {print "\n<li><em>Graduated:</em> $rest"; next;}
  if ($tag eq 'OCCU') {print "\n<li><em>Occupation:</em> $rest"; next;}
  if ($tag eq 'RELI') {print "\n<li><em>Religion:</em> $rest"; next;}
  if ($tag eq 'REFN') {print "\n<li><em>Reference:</em> $rest"; next;}
  if ($tag eq 'NOTE') {
    print "\n<li><em>Notes:</em><blockquote>\n";
    $req='</blockquote>';
    $lastlvl=$lvl;
    if ($rest=~/@(\S+)@/o) {
      &DoNotes($rest);
    } else {
      print "$rest";
    }
    next;
  }
  if ($tag eq 'PAGE') {&AddSourceItem('Page:'); next;}
  if ($tag eq 'PHOT') {
    print "\n<IMG src=$WebSite/$WebIGMDir/$PictureDir/$rest alt=\"Picture $rest\" border=0><br><br>";
    next;
  }
  if ($tag eq 'TEXT') {&AddSourceItem('Text:'); next;}
  if ($tag eq 'QUAY') {&AddSourceItem('Quality:'); next;}
  if ($tag eq 'TITL') {&AddSourceItem('Title:'); next;}
  if ($tag eq 'TYPE') {print "\n<li><em>$rest:</em> "; next;}
#
# Check schema
#
  $label=$indischema{$tag};
  if ($label) {print "\n<li><em>$label:</em> $rest"; next};
#
# Tags from Family Tree Maker Program
#
  if ($tag eq '_FA1') {print "\n<li><em>Christened:</em> $rest"; next;}
  if ($tag eq '_FA2') {print "\n<li><em>Buried:</em> $rest"; next;}
  if ($tag eq '_FA3') {print "\n<li><em>Baptism:</em> $rest"; next;}
  if ($tag eq '_FA4') {print "\n<li><em>Fact 1:</em> $rest"; next;}
  if ($tag eq '_FA5') {print "\n<li><em>Fact 2:</em> $rest"; next;}
  if ($tag eq '_FA6') {print "\n<li><em>Occupation:</em> $rest"; next;}
  if ($tag eq '_FA7') {print "\n<li><em>Titles:</em> $rest"; next;}
  if ($tag eq '_FA8') {print "\n<li><em>Education:</em> $rest"; next;}
  if ($tag eq '_FA9') {print "\n<li><em>SSN:</em> $rest"; next;}
  if ($tag eq '_FA10') {print "\n<li><em>Last Residence:</em> $rest"; next;}
  if ($tag eq '_FA11') {print "\n<li><em>State of Issue:</em> $rest"; next;}
  if ($tag eq '_FA12') {print "\n<li><em>Zip of Payment:</em> $rest"; next;}
  if ($tag eq '_FA13') {print "\n<li><em>Military Service:</em> $rest"; next;}
  if ($tag eq '_MREL') {print "\n<li><em>Relationship to Mother:</em> $rest"; next;}
  if ($tag eq '_FREL') {print "\n<li><em>Relationship to Father:</em> $rest"; next;}

  print "\n<li><em>$tag:</em> $rest" if ($rest ne '');
}
print '</ul>';
#
# Handle Parents
#

$Gotparent='';
foreach $parent (@Parents) {
  ($key)=($parent=~/@(\S+)@/o);
  $key=$idx{$key};
  seek(GEDCOM,$key,0) || die "Can't seek to $key";
  <GEDCOM>;
  while (<GEDCOM>) {
    &IGMGetLine;
    last if ($lvl eq '0');
    if ($tag eq 'HUSB') {
      print "<br>\n<em>Father: </em>";
      $Gotparent='y';
      &DoParent($rest);
    } elsif ($tag eq 'WIFE') {
      $Gotparent='y';
      print "<br>\n<em>Mother: </em>";
      &DoParent($rest);
    }
  }
}

print "<br>\n";
#
# Handle Families
#
$kid=1;
$family=1;
@req=();
$Gotkid='';


foreach $child (@Children) {
  print "<br>\n<em>Family $family:</em> ";
  $family++;
  $GotSpouse='';
  ($child)=($child=~/@(\S+)@/o);
  @Temp=();
  seek(GEDCOM,$idx{$child},0) || die "Can't seek to $child";
  <GEDCOM>;
  $GotSource='';
  $lastlvl=0;
  while (<GEDCOM>) {
    &IGMGetLine;
    if ($lvl <= $lastlvl) {
      if ($GotSource) {
        print &AddSource;
        $GotSource='';
        $SourceText='';
      }
      if ($req[$lvl]) {
        print "$req[$lvl]";
        $req[$lvl]='';
      }
      $lastlvl=0;
    }
    last if ($lvl eq '0');
    $subject = trim($subject);
    $rest =  trim($rest);
    if ($tag eq 'CHIL') {push(@Temp,$rest); $Gotkid='y'; next;}
    if ($tag eq 'HUSB') {
      if ($rest ne $subject) {
        &DoParent($rest);
        $req[0]='</ul>';
        print "<ul>";
        $GotSpouse='y';
      }
      next;
    }
    if ($tag eq 'WIFE') {
      if ($rest ne $subject) {
        &DoParent($rest);
        $req[0]='</ul>';
        print "<ul>";
        $GotSpouse='y';
    }
      next;
    }
    if ($tag eq 'CONC') {
      if ($GotSource) {
        $SourceText.="$rest";
      } else {
        print "$rest";
      }
      next;
    }
    if ($tag eq 'CONT') {
      if ($GotSource) {
        $SourceText.="<br>\n$rest";
      } else {
        print "<br>\n$rest";
      }
      next;
    }
    if ($GotSpouse eq '') {
      print "\n<ul>";
      $req[0]='</ul>';
      $GotSpouse='y';
    }
    if ($tag eq 'DIV') {print "\n<li><em>Divorced:</em> $rest"; next;}
    if ($tag eq 'DIVF') {print "\n<li><em>Divorce Filed:</em> $rest"; next;}
    if ($tag eq 'ANUL') {
      print "\n<li><em>Annulment:</em> $rest";
      next;
    }
    if ($tag eq 'ENGA') {
      print "\n<li><em>Engagement:</em> $rest";
      next;
    }
    if ($tag eq 'CENS') {
      print "\n<li><em>Census:</em> $rest";
      next;
    }
    if ($tag eq 'MARB') {
      print "\n<li><em>Marriage Bann:</em> $rest";
      next;
    }
    if ($tag eq 'MARC') {
      print "\n<li><em>Marriage Contract:</em> $rest";
      next;
    }
    if ($tag eq 'MARL') {
      print "\n<li><em>Marriage License:</em> $rest";
      next;
    }
    if ($tag eq 'MARR') {
      print "\n<li><em>Married:</em> $rest";
      next;
    }
    if ($tag eq 'MARS') {print "\n<li><em>Marriage Settlement:</em> $rest"; next;}
    if ($tag eq 'DATE') {print " $rest"; next;}
    if ($tag eq 'PLAC') {print " in $rest"; next;}
    if ($tag eq 'SOUR') {
#      print "\n<li><em>Source</em>" if ($lasttag eq 'NAME');
      $GotSource='y';
      $lastlvl=$lvl;
      if ($rest=~/@(\S+)@/o) {
        &DoNotes($rest);
      } else {
       $SourceText=$rest;
      }
      next;
    }
    if ($tag eq 'PAGE') {&AddSourceItem('Page:'); next;}
    if ($tag eq 'TEXT') {&AddSourceItem('Text:'); next;}
    if ($tag eq 'QUAY') {&AddSourceItem('Quality:'); next;}
    if ($tag eq 'TITL') {&AddSourceItem('Title:'); next;}
    if ($tag eq 'NOTE') {
      print "\n<li><em>Notes:</em><blockquote>\n";
      $req[$lvl]='</blockquote>';
      $lastlvl=$lvl;
      if ($rest=~/@(\S+)@/o) {
        &DoNotes($rest);
      } else {
        print "$rest";
      }
      next;
    }
    $label=$famschema{$tag};
    print "\n<li><em>$label:</em> $rest" if ($label);
  }
  print $req[0] if ($req[0] ne '');
  print '<ol>';
#
# Now print children's names and birthdates
#
  foreach $child (@Temp) {
    print "\n<li>";
    &DoParent($child);
  }
  print '</ol>';
}


if ($SourceNo > 0) {
  print "<br>\nSources:<br>\n<ol>\n";
  $SourceNo=0;
  foreach $SourceText (@Sources) {
    $SourceNo++;
    print "<A NAME=\"S$SourceNo\"></NAME><li>";
    if ($SourceText=~/@(\S+)@/o) {
      &DoNotes($rest);
    } else {
      print "$SourceText";
    }
  }
}
print "</ul><br>\n";
#
# URL Encode Savename into EncodeName
#
$EncodeName=&escape($Savename);
#
# If links are allowed the show them and allow additions
#


if ($AllowLinks) {
  print "<h2>Links:</h2>\n";
  if (open(LINK,"$LocIGMDir/$DB/$DB-$focus.lnk")) {
    while (<LINK>) {
      (($url,$desc)=/(.*)\|(.*)/);
#
# Handle old style links if they exist.
#
      if ($url eq '') {
        (($url,$desc)=/(.*)\,(.*)/);
      }
      print "<A HREF=\"$url\">$desc</A><BR>\n";
    }
    print "<br>\n";
  }
}
print "<HR><CENTER><B><A HREF=\"$WebSite/$WebIGMDir/$DB/$DB.html\">Master Index</A>\n";
if ($Gotparent) {
  print " | <A HREF=$WebCGIDir/$PedScript/n=$DB?$focus>Pedigree Chart</A>\n";
}
if ($Gotkid) {
  print " | <A HREF=$WebCGIDir/$DescScript/n=$DB?$focus>Descendency Chart</A>\n";
}
#
# If GEDCOM extraction is allowed the show them and allow additions
#
if ($AllowGED) {
  print " | <a href=$WebCGIDir/$GedScript?Database=$DB&Subject=$focus&Name=$EncodeName>Extract GEDCOM</a></B></CENTER>\n";
}
if ($AllowLinks) {
  print "|<a href=$WebSite/$WebCGIDir/$LinkScript?Database=$DB&Subject=$focus&Name=$EncodeName>Add a Link</a>\n";
}

print "\n";
&counter;
&IGMEnd;

dbmclose(%idx) if ($UseDBM);
$time=(times)[0]-$starttime;
&IGMLog("Individual $Savename accessed by $ENV{\"REMOTE_ADDR\"} $ENV{\"HTTP_USER_AGENT\"} using $time");
#
# Subroutine to print name and birthdate
#
sub DoParent {
  ($key)=@_;
  $oldseek=tell;
  ($key)=($key=~/@(\S+)@/o);
  $seek=$idx{$key};
  $key=$seek unless ($UseXrefTags);
  seek(GEDCOM,$seek,0) || die "Can't seek to $key";
  $type='';
  $output='';
  <GEDCOM>;
  while (<GEDCOM>) {
    &IGMGetLine;
    last if ($lvl eq '0');
    if ($tag eq 'NAME') {
      $rest=~s|/||go;
      print "<A HREF=$WebCGIDir/$GetScript/n=$DB?$key>$rest</A>";
    }
    if ($type eq 'BIRT') {
      $output=$rest if ($tag eq 'DATE');
      if ($tag eq 'PLAC') {
        $output.=' ' if ($output);
        $output.="in $rest";
      }
    }
    $type=$tag if ($rest eq '');
  }
  print ", b. $output" if ($output);
  seek(GEDCOM,$oldseek,0) || die "Can't seek to $oldseek";
}

#
# Subroutine to print notes via Xref tag
#
sub DoNotes {
  ($key)=@_;
  local($oldseek)=tell;
  ($key)=($key=~/@(\S+)@/o);
  seek(GEDCOM,$idx{$key},0) || die "Can't seek to $key";
  $_=<GEDCOM>;
  &IGMGetLine;
  if ($rest=~/^NOTE (.*)/) {
    if ($GotSource) {
      $SourceText.=$1;
    } else {
      print $1;
    }
  }
  while (<GEDCOM>) {
    &IGMGetLine;
    last if ($lvl eq '0');
    if ($tag eq 'CONC') {
      if ($GotSource) {
        $SourceText.="$rest";
      } else {
        print "$rest";
      }
      next;
    }
    if ($tag eq 'CONT') {
      if ($GotSource) {
        $SourceText.="<br>\n$rest";
      } else {
        print "<br>\n$rest";
      }
      next;
    }
    if ($tag eq 'TITL') {&AddSourceItem('Title:'); next;}
    if ($tag eq 'AUTH') {&AddSourceItem('Author:'); next;}
    if ($tag eq 'PUBL') {&AddSourceItem('Publication:'); next;}
    if (($tag eq 'CALN') && ($rest)) {&AddSourceItem('Call Number:'); next;}
    if ($tag eq 'MEDI') {&AddSourceItem('Media:'); next;}
    if ($tag eq 'NOTE') {
      if ($GotSource) {
        $SourceText.='<br>' if ($SourceText);
        $SourceText.="Note: ";
      } else {
        print " Note: ";
      }
      if ($rest=~/@(\S+)@/o) {
        &DoNotes($rest);
      } else {
        if ($GotSource) {
          $SourceText.="$rest";
        } else {
          print "$rest";
        }
      }
      next;
    }
    &AddSourceItem("$tag");
  }
  seek(GEDCOM,$oldseek,0) || die "Can't seek to $oldseek";
}
#
# Subroutine to print source or footnote of source
#
sub AddSource {
  if ($InlineSource) {
    return "[source: $SourceText]";
  } else {
    $i=1;
    foreach $s (@Sources) {
      return "<A HREF=\"#S$i\"><SUP>$i</SUP></A>" if ($s eq $SourceText);
      $i++;
    }
    push(@Sources,$SourceText);
    $SourceNo++;
    return "<A HREF=\"#S$SourceNo\"><SUP>$SourceNo</SUP></A>";
  }
}

sub AddSourceItem {
  ($t)=@_;
  if ($GotSource) {
    $SourceText.='<br>' if ($SourceText);
    $SourceText.="$t $rest";
  } else {
    print "\n<li><em>$t</em> $rest";
  }
}

sub trim($)
{
   my $string = shift;
   $string =~ s/^\s+//;
   $string =~ s/\s+$//;
   return $string;
}

