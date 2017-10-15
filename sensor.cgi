#!/usr/bin/perl
use strict;
use warnings;
$|++;

use CGI qw();
use Fcntl;

my $CGI_TO_SENSORD_PIPE = "/tmp/cgi_to_sensord.pipe";
my $SENSORD_TO_CGI_PIPE = "/tmp/sensord_to_cgi.pipe";
my $PHOTO_DIR = "/var/www/sensor/photos";

my $cgi = CGI->new;
print $cgi->header('text/plain');
if ('POST' eq $cgi->request_method && $cgi->param('action')) {
    my $status = &checkSensorProcess();
    if ($cgi->param('action') eq "arm") {
        if ($status eq "down") {
            print $status;
        }
        else {
            &writePipe("arm");
            print &checkSensorStatus();
        }
    }
    elsif ($cgi->param('action') eq "disarm") {
        if ($status eq "down") {
            print $status;
        }
        else {
            &writePipe("disarm");
            print &checkSensorStatus();
        }
    }
    elsif ($cgi->param('action') eq "status") {
        if ($status eq "down") {
            print $status;
        }
        else {
            &writePipe("status");
            print &checkSensorStatus();
        }
    }
    elsif ($cgi->param('action') eq "getLatestPhoto") {
        print &getLatestPhoto();
    }
}
else {
    print "ERROR: wrong request type and/or parameters\n";
}

#---<subroutines>--------------------------------------------------------------

sub writePipe() {
    my $msg = shift;
    sysopen (my $FIFO, $CGI_TO_SENSORD_PIPE, O_NONBLOCK|O_WRONLY) or die "Couldn't open $CGI_TO_SENSORD_PIPE, $!";
    syswrite ($FIFO, $msg);
    close ($FIFO) or die "Couldn't close $CGI_TO_SENSORD_PIPE"; #TODO: make a subroutine to print error and exit (open and close)
}

sub checkSensorProcess() {
    my @psArray = `pgrep sensord`;
    (scalar @psArray == 0) ? return "down" : return "running";
}

sub checkSensorStatus() {
    return "down" if (&checkSensorProcess eq "down");
    my $output;
    sysopen (my $FIFO, $SENSORD_TO_CGI_PIPE, O_RDONLY) or die "Couldn't open pipe $SENSORD_TO_CGI_PIPE, $!";
    my $return = sysread ($FIFO, $output, 12); 
    close ($FIFO) or die "Couldn't close pipe $SENSORD_TO_CGI_PIPE";
    #FIXME: Probably should check return, incase of EAGAIN, etc.
    if ($output =~ "armed") {
        return $output;
    }
    else {
        return "ERROR: sensor status is unknown";
    }
}

sub getLatestPhoto() {
    my $latestPhoto = `/bin/ls -ltr /var/www/sensor/photos | awk '{print \$9}' | tail -1`;
    chomp $latestPhoto;
    return $latestPhoto;
}

