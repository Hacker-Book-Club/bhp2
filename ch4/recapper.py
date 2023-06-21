from scapy.all import TCP, rdpcap
import collections
import os
import re
import sys
import zlib

# 1) Set up the location of directories in which we output the images and the locations of the pcap file to read in
OUTDIR = "/root/Desktop/pictures"
PCAPS = "/root/Downloads"

# 2) Define the namedtuple, Response, with two attributes: packet header and payload
Response = collections.namedtuple("Response", ["header", "payload"])


# 3) Helper function to get the packet header
def get_header(payload):
    try:
        # 1) This matches and extracts the header by looking for \r\n (carriage return + new line) pairs
        header_raw = payload[: payload.index(b"\r\n\r\n") + 2]
    except ValueError:
        sys.stdout.write("-")
        sys.stdout.flush()
        # 2) Payload does not match expected format. Value error is thrown ^ (The return here ends the get_header function)
        return None

    # 3) Splits the payload into key value pair and puts it in a dict
    header = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", header_raw.decode()))
    # 4) If we do not find it, return `None`
    if "Content-Type" not in header:
        return None
    return header


# 4) Extracting the contents from the packet to reconstitute the images
def extract_content(Response, content_name="image"):
    content, content_type = None, None
    # 1) Any response where the content-type is image will be caught here. ex: png/jpg
    if content_name in Response.header["Content-Type"]:
        # 2) Store actual content type from the header after first slash. split: notstored/stored -> "[0]=[notstored]/[1]=[stored]"
        content_type = Response.header["Content-Type"].split("/")[1]
        # 3) This holds the content, everything after the header
        content = Response.payload[Response.payload.index(b"\r\n\r\n") + 4 :]

        # 4) If the content has been encoded, we decompress it using zlib
        if "Content-Encoding" in Response.header:
            if Response.header["Content-Encoding"] == "gzip":
                content = zlib.decompress(Response.payload, zlib.MAX_WBITS | 32)
            elif Response.header["Content-Encoding"] == "deflate":
                content = zlib.decompress(Response.payload)

    # 5) Return the tuple with content and content_type
    return content, content_type


class Recapper:
    # 1) Initialize the object with the name of the pcap file to read
    def __init__(self, fname):
        pcap = rdpcap(fname)
        # 2) Use Scapy to separate each TCP session automatically into a dictionary with the complete streams. SICCC DUDE
        self.sessions = pcap.sessions()
        # 3) Create an empty list called responses to fill with responses from the pcap
        self.responses = list()

    # 5) Reads the responses from the pcap file
    def get_responses(self):
        # 1) Iterate over the sessions dictionary
        for session in self.sessions:
            payload = b""
            # 2) Then iterate over packets in each session
            for packet in self.sessions[session]:
                try:
                    # 3) filter the traffic so we only get packets with dst or src of port 80. Concatenate the payload of all traffic into a single buffer called payload
                    if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                        payload += bytes(packet[TCP].payload)
                except IndexError:
                    # 4) If there is no TCP traffic we will print an x and keep going
                    sys.stdout.write("x")
                    sys.stdout.flush()
            if payload:
                # 5) After reassembling HTTP data, if we have a payload, send it to the header-parsing function
                header = get_header(payload)
                if header is None:
                    continue
                # 6) append the response to the responses list made earlier
                self.responses.append(Response(header=header, payload=payload))

    # 6) writes image files, contained in the responses, to the output dir
    def write(self, content_name):
        # 1) Iterate over responses
        for i, responses in enumerate(self.responses):
            # 2) Extract the content from them
            content, content_type = extract_content(response, content_name)
            if content and content_type:
                # files will be written as ex_{#}.{png|jpg}
                fname = os.path.join(OUTDIR, f"ex_{i}.{content_type}")
                print(f"Writing {fname}")
                with open(fname, "wb") as f:
                    # 3) Write it to the file
                    f.write(content)


if __name__ == "__main__":
    pfile = os.path.join(PCAPS, "pcap.pcap")
    recapper = Recapper(pfile)
    recapper.get_responses()
    recapper.write("image")
