#!/usr/bin/perl
#
# igmped, 16 Sep 1996, by Randy Winch <gumby@edge.net>
#
#############################################################################
#
# This program provides for on-the-fly pedigree chart generation
#
#############################################################################
use Math::BigInt;
use Config;
#use integer qw(64bit);

$Program = 'IGMPed';
$Version = '1.2';
require 'igmini';
require 'igmlib';
$starttime=(times)[0];
#my $parities;
#$parities = Math::BigInt->new(0);
my $Savename;
#
sub trim($);
$tmp=$ENV{'PATH_INFO'};
(($temppeddepth)=($tmp=~m#^/n=(.*)#)) || &IGMDie( "PATH_INFO \"$tmp\" not in correct format.");
#

if ($temppeddepth eq 'GroatFamily'){
   $Peddepth = 10;
}else{
   $Peddepth = $temppeddepth;
}
#$Peddepth=10;
$DB='GroatFamily';
$tmp=$ENV{'QUERY_STRING'};
(($key) = ($tmp =~ /(\w+)/)) || &IGMDie( "QUERY_STRING \"$tmp\" not in correct format.");
$focus=$key;

#
# Load index into assoc array idx or use DBM file
#
if ($UseDBM) {
  dbmopen(%idx,"$LocIGMDir/$DB/$DB",undef) || die 'Cannot open dbm file';
} else {
  open(INDEX,"/nfs/notrust/cgi-bin/mgroat/GroatFamily.idx") || &IGMDie("Can't open index");
  while (<INDEX>) {
    /^(\S+) (.*)/o;
    $idx{$1}=$2;
  }
  close(INDEX);
}
$key=$idx{$key} if ($UseXrefTags);
open(GEDCOM,"/nfs/notrust/cgi-bin/mgroat/GroatFamily.ged") || die "Can't open GEDCOM";
seek(GEDCOM,$key,0);
$_=<GEDCOM>;
($subject)=/^\d+\s+@(\w+)@\s+.*$/;
#i$level = Math::BigInt->new();
$level=-1;
$maxlevel=$Peddepth-1;
$maxlevel=200;
$line_num = 1;
$array_size = 14000;
$pedigreestring = '';

@appeared_or_not = (0) x $array_size;
#@ancestors_line_number = (0,0) x $array_size;

&HTMLStart;

print "<HTML>\n<HEAD>\n<TITLE>Michael M. Groat's Genealogical Database $Title</TITLE>\n";

&Doindividual($subject,0);

print "<script type=\"text/javascript\" language=\"JAVASCRIPT\"> \n";

$array_string = "  var ancestors_line_number=[[0,0],[";
for ($index = 1; $index <= $line_num - 1; $index++){
   $array_string .= $ancestors_line_number[$index][0];
   $array_string .= ",";
   $array_string .= $ancestors_line_number[$index][1];
   $array_string .= "],[";
}
$array_string .="0,0]];\n";
print $array_string;

print "   function formHandler(thisItem) {\n";
print "      var URL = 'http://cgibin.cs.unm.edu/mgroat-bin/igmped.cgi/n' + thisItem.options[thisItem.selectedIndex].value + '?$focus'; ";
print "      if(URL != \"\"){ window.location.href = URL; } \n";
print "   }\n";
print "   function hidebranches(line_num, main,closeorexpand = 0) {\n";
print "      var x = document.getElementById(\"ButtonID\" + line_num ).innerHTML;\n";
print "      if (main === 1) {\n";
print "         if (x != \"+\") { \n";
print "            document.getElementById(\"ButtonID\" + line_num ).innerHTML = \"+\";\n";
print "            closeorexpand = 0;\n";
print "         } else { \n";
print "            document.getElementById(\"ButtonID\" + line_num ).innerHTML = \"-\";\n";
print "            closeorexpand = 1;\n";
print "         }\n";
print "      }\n";
print "      var father_line_number = ancestors_line_number[line_num][0];\n";
print "      if (father_line_number > 0) {\n";
print "         toggle(\"DivID\" + father_line_number,closeorexpand);\n";
print "         if ((ancestors_line_number[father_line_number][0] != 0 ) || (ancestors_line_number[father_line_number][1] != 0)) {\n";
print "            var y = document.getElementById(\"ButtonID\" + father_line_number ).innerHTML;\n";
print "            if (y != \"+\") {\n";
print "               hidebranches(father_line_number,0,closeorexpand);\n";
print "            }\n";
print "         }\n";
print "      }\n";
print "      var mother_line_number = ancestors_line_number[line_num][1];\n";
print "      if (mother_line_number > 0) {\n";
print "         toggle(\"DivID\" + mother_line_number,closeorexpand);\n";
print "         if ((ancestors_line_number[mother_line_number][0] != 0 ) || (ancestors_line_number[mother_line_number][1] != 0)) {\n";
print "            var z = document.getElementById(\"ButtonID\" + mother_line_number ).innerHTML;\n";
print "            if (z != \"+\") {\n";
print "               hidebranches(mother_line_number,0,closeorexpand);\n";
print "            }\n";
print "         }\n";
print "      }\n";
print "   }\n";
print "   function toggle(elementname,onoff) { ";
print "      var x = document.getElementById(elementname);";
print "      if (onoff === 0) {";
print "         x.style.display = 'none';";
print "      } else { ";
print "         x.style.display = 'inline'; ";
print "      } ";
print "   }";
print "</script>";

print "<style>";
print " div { display:inline; } \n";
#print " button { height:15px; width:15px; text-align:center;}\n";
print "</style>";

print "</HEAD>\n<BODY ";
print "BACKGROUND=\"$WebSite/$WebIGMDir/$Back\"" if ($Back ne '');
print "BGCOLOR=$BGColor TEXT=$Text LINK=$Link VLINK=$VLink>\n";
print "<CENTER><H2>Michael M. Groat's Genealogical Database</H2></CENTER>\n";
print "<CENTER><B>Entries:</B> 13347 &nbsp;&nbsp;<B>Updated:</B> March 31, 2013 </CENTER>";
print "<CENTER><B>Contact:</B> <A href=\"mailto:mgroat#AT#cs#DOT#unm#DOT#edu\">Michael M. Groat</A> &nbsp;&nbsp <B>Home Page:</B> <A href=\"http://www.cs.unm.edu/~mgroat\">Michael M. Groat's CS Homepage</A></CENTER>";
print "<CENTER><H3>$Title</H3></CENTER><HR>\n";
print $pedigreestring;
print "</div></pre><br>\n";

#
# URL Encode $Savename
#
$EncodeName=&escape($Savename);

print "<hr><CENTER><B><A HREF=\"$WebSite/$WebIGMDir/$DB/$DB.html\">Master Index</A>\n";
print " | <A HREF=$WebCGIDir/igmget.cgi/n=$DB?$focus>Individual</A>";
print " | <A HREF=$WebCGIDir/$DescScript/n=$DB?$focus>Descendency Chart</A>\n";

#
# If GEDCOM extraction is allowed the show them and allow additions
#
if ($AllowGED) {
  print " | <a href=$WebCGIDir/$GedScript?Database=$DB&Subject=$focus&Name=$EncodeName&type=descendants>Extract GEDCOM</B></CENTER></a>\n";
}

&counter;
&IGMRKW;
dbmclose(%idx) if ($UseDBM);
$time=(times)[0]-$starttime;
&IGMLog("Pedigree $Savename accessed by $ENV{\"REMOTE_ADDR\"} $ENV{\"HTTP_USER_AGENT\"} using $time");

#
# recursive subroutine to do individual
#
sub Doindividual {

  # local($parities) = Math::BigInt->new();
  local ($key,$parities)=@_;
  local $tempkey = substr $key, 1;
  local $temptempkey = $key;
  local $mylinenumber = 0;
  local $mother_line_number = 0;
  local $father_line_number = 0;
  local ($name)='';
  local ($family)='';
  local ($birth)='';
  local ($death)='';
  local ($type)='';
  local $num_ancestors=0;

  $level++;
  if ($level<=$maxlevel) {

    #
    # Ignore seeks to top of file
    #
    if ($key ne '') {
      $seek=$idx{$key};
      $key=$seek unless ($UseXrefTags);
      seek(GEDCOM,$seek,0) || die "Cannot seek to $key";
      <GEDCOM>;
      while (<GEDCOM>) {
        &IGMGetLine;
        if ($lvl eq '1'){ $type = $tag;}
        last if ($lvl eq '0');
        if ($tag eq 'NAME') {
          $rest=~s|/| |g;
          $rest=~s/\s{2,}/ /g;
          $rest=~s/ ,/,/g;
          $rest = trim($rest);
          $name=$rest;
          if ($level==0) {

            $pedigreestring .= "<h1>Ancestors of $name</h1><hr>\n";
            $pedigreestring .= "<CENTER><B><A HREF=\"$WebSite/$WebIGMDir/$DB/$DB.html\">Master Index</A>\n";
            $pedigreestring .= " | <A HREF=$WebCGIDir/igmget.cgi/n=$DB?$focus>Individual</A>\n";
            $pedigreestring .= " | <A HREF=$WebCGIDir/$DescScript/n=$DB?$focus>Descendency Chart</A>\n";

            if ($AllowGED) {
               $pedigreestring .=  " | <a href=$WebCGIDir/$GedScript?Database=$DB&Subject=$focus&Name=$EncodeName&type=descendants>Extract GEDCOM</a>\n";
            }
            $pedigreestring .=  "</B></CENTER><hr>";
            # print "<CENTER>";
            # print "<FORM>If this page takes too long to download you can change the depth of the pedigree here &nbsp;&nbsp;<SELECT name=\"tblofContents\" onChange=\"javascript:formHandler(this)\">";
            # print "<OPTION>Select Depth</OPTION>";
            # print "<OPTION value=\"$MY_NAME=5\">5</OPTION>";
            # print "<OPTION value=\"$MY_NAME=10\">10</OPTION>";
            # print "<OPTION value=\"$MY_NAME=15\">15</OPTION>";
            # print "<OPTION value=\"$MY_NAME=20\">20</OPTION>";
            # print "<OPTION value=\"$MY_NAME=25\">25</OPTION>";
            # print "<OPTION value=\"$MY_NAME=30\">30</OPTION>";
            # print "<OPTION value=\"$MY_NAME=35\">35</OPTION>";
            # print "<OPTION value=\"$MY_NAME=40\">40</OPTION>";
            # print "<OPTION value=\"$MY_NAME=45\">45</OPTION>";
            # print "<OPTION value=\"$MY_NAME=50\">50</OPTION>";
            # print "<OPTION value=\"$MY_NAME=55\">55</OPTION>";
            # print "<OPTION value=\"$MY_NAME=60\">60</OPTION>";
            # print "<OPTION value=\"$MY_NAME=200\">200</OPTION>";
            # print "</SELECT></FORM>";
            # print "</CENTER><HR>";
            $pedigreestring .=  "<PRE><div id='DivID1'>";
            $Savename=$rest;
          }
          next;
        }
        if ($tag eq 'DATE') {
          # print "In date $rest $type";
          $birth=$rest if ($type eq 'BIRT');
          $death=$rest if ($type eq 'DEAT');
          $birth = trim($birth);
          $death = trim($death);
          next;
        }
        #        if ($tag eq 'PLAC') {
        #          if ($type eq 'BIRT') {
        #            print "Inside birth $rest";
        #            if ($birth eq '') {
        #              $birth="$rest";
        #            } else {
        #              $birth.=" $rest";
        #            }
        #          }
        #          if ($type eq 'DEAT') {
        #            if ($death eq '') {
        #              $death="$rest";
        #            } else {
        #              $death.=" $rest";
        #            }
        #          }
        #          $death = trim($death);
        #          $birth = trim($birth);
        #          next;
        #        }
        if ($tag eq 'FAMC') {
          ($family)=($rest=~/@(\w+)@/o);
          next;
        }
      } continue {
        $type=$tag if ($rest eq '');
      }
    } else {
       $pedigreestring .=  "Key is ne";
    }

    # Traverse ancestor tree, males first
    $mother_line_number = 0;
    $father_line_number = 0;
    if (@appeared_or_not[$tempkey] == 0) {
       $father_line_number = &Dofamily($family,'HUSB',$parities,1);
    }
    $ancestors_line_number[$line_num][0] = $father_line_number;
    if ($level==0) {
       $pedigreestring .=  "<button id=\"ButtonID" . $line_num . "\" onclick=\"hidebranches(" . $line_num . ",1)\">-</button> 1 <A HREF=$WebCGIDir/$GetScript/n=$DB?$key>$name</A>"; #unless ($name eq '');
    } else {
       $pedigreestring .=  '     ';
       # print "paraties is $parities level is $level";
       # $temp1 = $parities | (1 << $level);
       # $temp2 = $parities | (2**$level);
       # print "temp1 is $temp1 temp2 is $temp2 level is $level par is $parities";
       &PedIndent($parities,$level);
       if ($top) {
          $pedigreestring .=  '/';
       } else {
          $pedigreestring .=  '\\';
       }
       $mytemp = $level + 1;
       $pedigreestring .=  "-- <button id=\"ButtonID" . $line_num . "\" onclick=\"hidebranches(" . $line_num . ",1)\">-</button> $mytemp <A HREF=$WebCGIDir/$GetScript/n=$DB?$key>$name</A>"; # unless ($name eq '');
    }
    $pedigreestring .=  " b. $birth" if ($birth ne '');
    $pedigreestring .=  " d. $death" if ($death ne '');
    # print "$key";
    if (@appeared_or_not[$tempkey] == 0){
       $pedigreestring .= "<A NAME=\"$temptempkey\"></A>";
    } else {
       $pedigreestring .= " <A HREF=\"#$temptempkey\">(Person is repeated. Click for first appearance.)</A>";
    }

    # print " <A HREF=$WebCGIDir/$PedScript/n=$DB?$key>=></A>" if (($family) && ($level==$maxlevel));
    $mylinenumber = $line_num;
    $line_num++;
    $pedigreestring .=  "\n</div><div id='DivID" . $line_num . "'>";
  }

  if(@appeared_or_not[$tempkey] == 0) {
     $temp = Math::BigInt->new($parities);
     $temp2 = Math::BigInt->new($level);
     $temp3 = Math::BigInt->new(1);
     $temp->bior($temp3->blsft($temp2));
     $mother_line_number = &Dofamily($family,'WIFE',$temp,0);
  }
  $ancestors_line_number[$mylinenumber][1] = $mother_line_number;
  if ($mother_line_number == 0){
     if($father_line_number == 0){
        $pedigreestring =~ s/<button\sid="ButtonID${mylinenumber}"\sonclick="hidebranches\(${mylinenumber},1\)">\-<\/button>//g;
     }
  }
  # print " tempkey is $tempkey ";
  @appeared_or_not[$tempkey] = 1;
  $level--;
  return $mylinenumber;
}

sub Dofamily {
  #  local($parities) = Math::BigInt->new();
  local ($family,$findtag,$parities,$top)=@_;
  # print "paritiesfam is $parities";
  $next='';
  local ($key)='';
  $key=$idx{$family};
  local $ancestor_line = 0;
  seek(GEDCOM,$key,0) || die "Cannot seek to $key";
  <GEDCOM>;
  while (<GEDCOM>) {
    &IGMGetLine;
    last if ($lvl eq '0');
    if ($tag eq $findtag) {
      ($next)=($rest=~/@(\w+)@/o);
      unless($Pedfull){
         $ancestor_line = &Doindividual($next,$parities);
      }
      last;
    }
  }
  if ($Pedfull) {
    $ancestor_line = &Doindividual($next,$parities);
  }
  return $ancestor_line;
}

sub PedIndent {
  ($parities,$level)=@_;

  for($i=1;$i<$level;$i++) {
     $temp6 = Math::BigInt->new(1)->blsft($i-1);
     $temp8 = Math::BigInt->new(1)->blsft($i);
     #     $p =$parities & (1 << ($i-1))?(~0):0;
     #     $q =$parities & (1 << $i)?(~0):0;
     $p = $parities & $temp6?(~0):0;
     $q = $parities & $temp8?(~0):0;

     if ($p ^$q) {
       $pedigreestring .= '|';
     } else {
       $pedigreestring .= ' ';
     }
     $pedigreestring .= '       ';
  }
}

sub trim($)
{
   my $string = shift;
   $string =~ s/^\s+//;
   $string =~ s/\s+$//;
   return $string;
}
