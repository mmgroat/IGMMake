#!/usr/bin/perl
######################################################################
# Guestbook                               Version 1.1                #
# Copyright 1999 Frederic TYNDIUK (FTLS)  All Rights Reserved.       #
# E-Mail: tyndiuk@ftls.org                Script License: GPL        #
# Created  05/30/99                       Last Modified 05/30/99     #
# Scripts Archive at:                     http://www.ftls.org/cgi/   #
######################################################################
# Function :                                                         #
# A Gestbook...                                                      #
######################################################################
##################### license & copyright header #####################
#                                                                    #
#                Copyright (c) 1999 by TYNDIUK Frederic              #
#                                                                    #
#  This program is free software; you can redistribute it and/or     #
#  modify it under the terms of the GNU General Public License as    #
#  published by the Free Software Foundation; either version 2 of    #
#  the License, or (at your option) any later version.               #
#                                                                    #
#  This program is distributed in the hope that it will be useful,   #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of    #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     #
#  GNU General Public License for more details.                      #
#                                                                    #
#  You should have received a copy of the GNU General Public License #
#  along with this program in the file 'COPYING'; if not, write to   #
#  the Free Software Foundation, Inc., 59 Temple Place - Suite 330,  #
#  Boston, MA 02111-1307, USA, or contact the author:                #
#                                                                    #
#                              TYNDIUK Frederic <tyndiuk@ftls.org>   #
#                                       <http://www.ftls.org/>       #
#                                                                    #
################### end license & copyright header ###################
######################################################################
# Necessary Variables:                                               #
# The following variables should be set to define the locations      #
# and URLs of various files, as explained in the documentation.      #

print "Content-type: text/html\n\n";

require "cgi-lib.pl";

$GuestbookURL = "http://cgibin.cs.unm.edu/mgroat-bin/guestbook2.cgi"; # En: Guestbook's URL
                                                              # Fr: URL du Guestbook
$GuestbookRealPath = "/nfs/notrust/cgi-bin/mgroat/guestbook.html";      # En: Guestbook's Path
                                                              # Fr: chemin du fichier Guestbook

$Motif = "<!-- Value_Add_Comments -->";  # En: The next Comments will be insert here...
                                         # Fr: Motif ou ajouter le commentaire suivant.

@Referers    = ("http://cgibin.cs.unm.edu");  # En: URL(s) of serveur you can use this script.
                                         # Fr: URL(s) des serveurs pouvant utiliser ce script.

$WebmasterEMail = "webmaster\@ftls.org"; # En: Webmaster E-Mail.
                                         # Fr: l'E-Mail du Webmaster

# En: You can change all messages, edit it's...
%UsersMessages = ("InvData", "FTLS's Guestbooks<BR>Invalid Submit data",
                  "Thanks" , "FTLS's Guestbooks<BR>Thank You For Signing The Guestbook",
                  "Back"   , "Back");

# Fr: Pour utiliser les messages en francais, supprimer les commentaires...
#%UsersMessages = ("InvData", "FTLS's Guestbooks<BR>Données Incomplettes ou Invalides",
#                  "Thanks" , "FTLS's Guestbooks<BR>Merci d'avoir signer ce livre d'or.",
#                  "Back"   , "Retour");


# Options:
$UseLog = 1;      # Use Log File ? 1 = YES; 0 = NO
$LogFile = "/nfs/notrust/cgi-bin/mgroat/Guestbook-Log.txt";
	
# Nothing Below this line needs to be altered!                       #
######################################################################


&CheckReferer; 
	# En: Test who can access to this form.
	# Fr: Teste si l'utilisateur est autorise ou pas a utiliser ce script.

&ReadParse(*input);
$Name = $input{'Name'};
$EMail = $input{'EMail'}; 
$Title = $input{'Title'};
$Comment = $input{'Comment'};

@date= localtime(time); 
@Months = ('January','February','March','April','May','June','July','August','September','October','November','December');
$date[5] += 1900;
$Time = "$date[3] $Months[$date[4]] $date[5]";

    print &PrintHeader;

	if (($Name eq "") || (length($Name) > 100) || (length($Title) > 100) || ($Comment eq "") || (length($Comment) > 1000) || !(&ControlMail($EMail)) ) {
		&Error($UsersMessages{'InvData'},1);
		$LogTxt = "Invalid Submit data";
	} else {
		open(FILE,"$GuestbookRealPath") || &Error("Cannot Open Guestbook File: $GuestbookRealPath, Error: $!\n,1");
		@Guestbook = <FILE>;
		close(FILE);

		$Text = $Motif;
		$Text .= "<DL><DT><A HREF=\"mailto:$EMail\">$Name</A><DD><B>$Title</B><BR>$Comment<BR>Date : $Time</DL>\n";

		$Result = "";
		foreach $GuestbookLine (@Guestbook) {
			$GuestbookLine =~ s/$Motif/\n$Text\n/;
			$Result .= $GuestbookLine;
		}

		open(FILE,">$GuestbookRealPath") || &Error("Cannot write Guestbook File: $GuestbookRealPath, Error: $!\n",1);
		print FILE $Result;
		close(FILE);

		print  HTMLHeaderTitle($UsersMessages{'Thanks'});
		print &Back($GuestbookURL);
		print &HTMLEnd;
		$LogTxt = "Add $Name";
	}

if ($UseLog) {
	open(LOG,">>$LogFile") || &Error("Cannot Write Log File : $LogFile, Error $!\n",1);
	print LOG "[$Time] - $ENV{'REMOTE_HOST'} $LogTxt\n";
	close(LOG);
}

# Sub

sub HTMLHeaderTitle {
	my($Title) = @_;
	return &HTMLHeader($Title).&Title($Title);
}

sub HTMLHeader {
	my($Title) = @_;
	$HeadTitle = $Title;
	$HeadTitle =~ s/\<\w\w*\>/ /gi;
    return <<EOF;
<HTML><HEAD><TITLE>The FTLS's $HeadTitle</TITLE>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
<META NAME="ROBOTS" CONTENT="NOINDEX, FOLLOW">
<META NAME="description" content="none">
<META NAME="keywords" content="none">
<META NAME="Author" CONTENT="FTLS (TYNDIUK Frederic, ftls\@ftls.org, http://www.ftls.org/)">
<META NAME="GENERATOR" CONTENT="CGI Script Made by FTLS"></HEAD>
<BODY BGCOLOR="#FFFFFF">
EOF
}

sub Title {
    my($Title) = @_ ;
    return <<EOF;
<BR><BR><P ALIGN="Center"><FONT FACE="Arial, helvetica" SIZE="+2" COLOR="#336699"><STRONG><EM>$Title</EM></STRONG></FONT></P><BR>
EOF
}

sub Back {
    my($url) = @_ ;
	return "<CENTER><BR><BR><FONT FACE=\"Arial\"><A HREF=\"$url\">$UsersMessages{'Back'}</A><BR><BR></CENTER>\n";
}

sub HTMLEnd {
    return <<EOF;
<CENTER><BR><BR>
	<FONT FACE="Arial" SIZE=-2>
	<EM>&copy Copyright 1999 <A HREF="http://www.ftls.org/ftls.shtml">FTLS</A> (<A HREF="mailto:ftls\@ftls.org">Tyndiuk Fr&eacute;d&eacute;ric</A>). All rights reserved.
	<BR>Send all comments to <A HREF="mailto:$WebmasterEMail">$WebmasterEMail</A>
	<BR>FTLS's CGI Scripts Archive : <A HREF="http://www.ftls.org/cgi/">http://www.ftls.org/cgi/</A></EM>
	</FONT>
</CENTER>
</BODY></HTML>
EOF
}

sub ControlMail {
	return @_[0] =~ /.+@.+\..+/;
}

sub Error {
	my($ErrorText, $Exit) = @_;
    print &HTMLHeaderTitle($ErrorText);
	print &Back($GuestbookURL);
	print &HTMLEnd;
	if($Exit) { exit; }
}

sub CheckReferer {
	if (defined $ENV{'HTTP_REFERER'}) {
		foreach $Referer (@Referers) {
			if ($ENV{'HTTP_REFERER'} =~ /^$Referer/i) {
				return;
        	}
		}
	}
	print &Error("Unauthorized access to: $ENV{'HTTP_REFERER'}",1);
}
