import pyshark
import subprocess, shlex, time, threading, queue

input_command = shlex.split('sudo tcpdump -AUtttvvvXXnns1024 -i lo0 port 9001 -l')
regex = shlex.split('egrep -o \"00:00:00.[0-9]+|val [0-9]+|ecr [0-9]+|length [0-9][0-9|3[0-9]30 3\w\w\w \w\w\w\w \w+|\w+.\w+.\w+.\w+.\w+ > \w+.\w+.\w+.\w+.\w+\"')
#input_command = 'sudo tcpdump -l -AUtttvvvXXnns1024 -i lo0 port 9001 | egrep -o \"00:00:00.[0-9]+|val [0-9]+|ecr [' \
                #'0-9]+|length [0-9][0-9|3[0-9]30 3\w\w\w \w\w\w\w \w+|\w+.\w+.\w+.\w+.\w+ > \w+.\w+.\w+.\w+.\w+\"'

#p1 = subprocess.Popen(input_command, stdout=subprocess.PIPE, universal_newlines=False)
#p2 = subprocess.Popen(regex, stdout=p1.stdout, universal_newlines=True)
#p2.wait(10)
#output = p2.communicate()[0]
#for row in output:
   # print(row)


def output_reader(p, out_queue):
    for line in iter(p.stdout.readline, b''):
        out_queue.put(line.decode('utf-8'))


def main():
    p = subprocess.Popen(input_command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    out_queue = queue.Queue()
    t = threading.Thread(target=output_reader, args=(p, out_queue))
    t.start()
    try:
        time.sleep(10)
        try:
            line = out_queue.get(block=False)
            print('got line from out_queue: {0}'.format(line), end='')
        except queue.Empty:
            print('could not get line from queue')
    finally:
        p.terminate()
        try:
            p.wait(timeout=1)
            print('== subprocess exited with rc =', p.returncode)
        except subprocess.TimeoutExpired:
            print('subprocess did not terminate in time')
    t.join()

main()
# sudo tcpdump -AUtttvvvXXnns1514 -i lo0 port 9001 -l | egrep -o "00:00:00.[0-9]+|val [0-9]+|ecr [0-9]+|length [6-9]+|3[0-9]30 3\w\w\w \w\w\w\w \w+|\w+.\w+.\w+.\w+.\w+ > \w+.\w+.\w+.\w+.\w+"

# p = subprocess.Popen(('sudo', 'tcpdump', '-AUtttvvvXXnns1514', '-i', 'lo0', 'port', '9001', '-l', '|', 'egrep', '-o', '\"00:00:00.[0-9]+|val [0-9]+|ecr [0-9]+|length [6-9]+|3[0-9]30 3\w\w\w \w\w\w\w \w+|\w+.\w+.\w+.\w+.\w+ > \w+.\w+.\w+.\w+.\w+\"'


def sniff_traffic_packets_cont():
    capture = pyshark.LiveCapture(interface='lo0', bpf_filter='tcp port 9001')
    capture.set_debug()
    for packet in capture.sniff_continuously():
        packet.ip.pretty_print()
        # print('Just arrived:', packet)
        # packet_capture = [packet.ip.len, packet.frame.time_delta, packet.tcp.srcport, packet.tcp.dstport, '0', packet.tcp.options.timestamp.tsval, packet.tcp.options.timestamp.tsecr]
        # print(packet_capture)
