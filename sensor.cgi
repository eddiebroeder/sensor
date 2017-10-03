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
    if ($cgi->param('action') eq "arm") {
        open (my $FIFO, ">", $CGI_TO_SENSORD_PIPE) or die "Couldn't open $CGI_TO_SENSORD_PIPE, $!";
        print $FIFO "arm";
        close ($FIFO) or die "Couldn't close $CGI_TO_SENSORD_PIPE"; #TODO: make a subroutine to print error and then exit (open and close)
        print &checkSensor();
    }
    elsif ($cgi->param('action') eq "disarm") {
        open (my $FIFO, ">", $CGI_TO_SENSORD_PIPE) or die "Couldn't open $CGI_TO_SENSORD_PIPE, $!";
        print $FIFO "disarm";
        close ($FIFO) or die "Couldn't close $CGI_TO_SENSORD_PIPE"; #TODO: make a subroutine to print error and then exit (open and close)
        print &checkSensor();
    }
    elsif ($cgi->param('action') eq "status") {
        print &checkSensor();
    }
    else {
        print "ERROR: wrong parameter value";
    }
}
else {
    print "ERROR: wrong request type and/or parameters\n";
}

#TODO XXX FIXME Should check if sensord is even running before trying to write to the pipe on line 16,22. or do a nonblocking write?
sub checkSensor() {
    my @psArray = `pgrep sensord`;
    return "down" if (scalar @psArray == 0);
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
