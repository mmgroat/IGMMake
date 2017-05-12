#!/usr/bin/perl
#
# igmlink, 16 Apr 1996, by Tim Doyle <tdoyle@doit.com>
#
#############################################################################
# - Change Log -
# Version 2.0  Added background
#              Added Copyright statement
# Version 2.1  Added Program & Version variables
#              Implemented IGM.PL library
#              Reorganized code
#              Enhanced Link screen layouts
#              Added igm.ini file - SL
#              Added linking to e-mail addresses
# Version 2.2  Renamed igm.ini to igmini
#              Renamed igm.pl to igmlib
# Version 2.2a Location variables modified - HM
#              Added directory for required files - BB
# Version 2.3  No changes
#
# Still to Do: Remove duplicate code (?? - BB)
#############################################################################
$Program = 'IGMLink';
$Version = '2.3';
require 'igmini';
require 'igmlib';
$|=1;

#if ( $ENV{ "REQUEST_METHOD" } ne "POST" ) {
#  &HTMLStart;
#  &IGMHeader( "Link Creation" );
#  print "There has been an error with the link process.\n";
#  print "Your link request was not processed.\n";
#  &IGMEnd;
#  exit 0;
#}

&LoadVars;
$DB=$FORM{"Database"};

if (($FORM{'URL'} eq '' ) && ($FORM{'EMAIL'} eq '')) {
  &HTMLStart;
  &IGMHeader( "Link Creation" );
  print "<P><FORM METHOD=\"POST\" ACTION=\"$LinkScript\">\n";
  print "<INPUT TYPE=\"HIDDEN\" NAME=\"Database\" VALUE=\"$FORM{\"Database\"}\">\n";
  print "<INPUT TYPE=\"HIDDEN\" NAME=\"Name\" VALUE=\"$FORM{\"Name\"}\">\n";
  print "<INPUT TYPE=\"HIDDEN\" NAME=\"Subject\" VALUE=\"$FORM{\"Subject\"}\">\n";

  print "This form will allow you to create a link from\n";
  print "<B>$FORM{\"Name\"}</B> in the <B>$NewTitle</B>\n";
  print "database to the same person in another database or to\n";
  print "your e-mail address.  This link will then become a\n";
  print "permanent part of this online database.  Anyone who views\n";
  print "the record for <B>$FORM{\"Name\"}</B> in the future will\n";
  print "see the link you have entered.  If the link is to another\n";
  print "database, the user will be able to instantly see this other\n";
  print "record and compare the information in the two databases.\n";
  print "If the link is to an e-mail address, the link will allow\n";
  print "users to send you an e-mail message for further information.\n";
  print "<P><HR>\n";
  print "<H2>Add a link for <B>$FORM{\"Name\"}</B> to an e-mail address.</H2>\n";
  print "Please enter your name \n";
  print "<INPUT TYPE=\"TEXT\" NAME=\"SUBM\" SIZE=\"50\">\n<P>";
  print "Please enter your e-mail address:  \n";
  print "<INPUT TYPE=\"TEXT\" NAME=\"EMAIL\" SIZE=\"50\">\n<BR><BR>";
  print "<INPUT TYPE=\"submit\" VALUE=\"Save Link\"><P>\n";
  print "<HR>\n";
  print "<H2>Add a link for <B>$FORM{\"Name\"}</B> to another database.</H2>\n";
  print "Please enter the name of the other database \n";
  print "<INPUT TYPE=\"TEXT\" NAME=\"URLDB\" SIZE=\"50\">\n<P>";
  print "Please enter the location (URL) for the person in the other database:  \n";
  print "<INPUT TYPE=\"TEXT\" NAME=\"URL\" SIZE=\"50\">\n";
  print "(Please enter full URL)\n<BR><BR>";
  print "<INPUT TYPE=\"submit\" VALUE=\"Save Link\">\n";
  print "</FORM>\n";
  &IGMEnd;
} else {
  $file = "$LocIGMDir/$FORM{\"Database\"}/$FORM{\"Database\"}-$FORM{\"Subject\"}.lnk";
  if ( -e $file ) {
    open (LINK,">> $file")
  } else {
    open (LINK,"> $file")
  }
  if ($FORM{"URL"} eq '') {
    print LINK "mailto:$FORM{\"EMAIL\"}|$FORM{\"SUBM\"} has more information on $FORM{\"Name\"} in an off-line Database\n";
  } else {
    print LINK "$FORM{\"URL\"}|$FORM{\"Name\"} in $FORM{\"URLDB\"} Database\n";
  }
  close (LINK);
  chmod (0666,$file);

  &HTMLStart;
  &IGMHeader('Link Creation');
  print "Your link has been saved<P>\n";
  print "Return to the record of";
  print "<A HREF=\"/$WebCGIDir/$GetScript/n=$FORM{\"Database\"}?$FORM{\"Subject\"}\">";
  print "$FORM{\"Name\"}</A>.";
  &IGMEnd;
}
