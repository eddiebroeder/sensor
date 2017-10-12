#!/usr/bin/perl
use strict;
use warnings;
$|++;

use CGI qw();
use Fcntl;

my $CGI_TO_SENSORD_PIPE = "/tmp/cgi_to_sensord.pipe";
my $SENSORD_TO_CGI_PIPE = "/tmp/sensord_to_cgi.pipe";

my $cgi = CGI->new;
print $cgi->header('text/plain');
if ('POST' eq $cgi->request_method && $cgi->param('action')) {
    if (&checkSensorProcess eq "down") {
        print "down";
        exit 0;
    }
    if ($cgi->param('action') eq "arm") {
        &writePipe("arm");
        #print &checkSensorStatus();
        print &checkSensorProcess();
    }
    elsif ($cgi->param('action') eq "disarm") {
        &writePipe("disarm");
        #print &checkSensorStatus();
        print &checkSensorProcess();
    }
    elsif ($cgi->param('action') eq "status") {
        print &checkSensorProcess();
    }
    else {
        print "ERROR: wrong parameter value";
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
    sleep 3; #XXX This is stupid to assume a certain duration
    my $output;
    sysopen (my $FIFO, $SENSORD_TO_CGI_PIPE, O_NONBLOCK|O_RDONLY) or die "Couldn't open pipe $SENSORD_TO_CGI_PIPE, $!";
    my $return = sysread ($FIFO, $output, 6); 
    close ($FIFO) or die "Couldn't close pipe $SENSORD_TO_CGI_PIPE";
    #FIXME: Probably should check return, incase of EAGAIN, etc.
    if ($output eq "armed" || $output eq "disarmed") {
        print $output;
    }
    else {
        print "ERROR: sensor status is unknown";
    }
}
