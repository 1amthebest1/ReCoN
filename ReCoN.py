import os
import subprocess

# Define the commands to install tools
def install_tools():
    print("Starting downloads...")

    # Update PATH for Go binaries
    go_install_path = "/home/user/go/bin"
    os.environ["PATH"] += os.pathsep + go_install_path

    # Install Go
    print("Installing Go...")
    subprocess.run("sudo rm -rf /usr/lib/go-1.19", shell=True, check=True)
    subprocess.run("wget https://go.dev/dl/go1.21.1.linux-amd64.tar.gz", shell=True, check=True)
    subprocess.run("sudo tar -C /usr/local -xzf go1.21.1.linux-amd64.tar.gz", shell=True, check=True)
    subprocess.run("echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc", shell=True, check=True)
    subprocess.run("source ~/.bashrc", shell=True, check=True)
    
    # Install httpx
    print("Installing httpx...")
    subprocess.run("git clone https://github.com/projectdiscovery/httpx.git", shell=True, check=True)
    subprocess.run("cd httpx && go mod tidy && go mod download && go build -o httpx ./cmd/httpx", shell=True, check=True)
    subprocess.run("sudo mv httpx /usr/local/bin/", shell=True, check=True)

    # Install subfinder
    print("Installing subfinder...")
    subprocess.run("wget https://github.com/projectdiscovery/subfinder/releases/download/v2.3.2/subfinder-linux-amd64.tar", shell=True, check=True)
    subprocess.run("tar -xzvf subfinder-linux-amd64.tar", shell=True, check=True)
    subprocess.run("sudo mv subfinder-linux-amd64 /usr/bin/subfinder", shell=True, check=True)

    # Install SecretFinder
    print("Installing SecretFinder...")
    subprocess.run("git clone https://github.com/m4ll0k/SecretFinder.git secretfinder", shell=True, check=True)
    subprocess.run("cd secretfinder && pip3 install -r requirements.txt", shell=True, check=True)
    
    # Install naabu
    print("Installing naabu...")
    subprocess.run("sudo apt-get -t bullseye-backports install -y libpcap-dev", shell=True, check=True)
    subprocess.run("go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest", shell=True, check=True)

    # Install uro
    print("Installing uro...")
    subprocess.run("pip3 install uro", shell=True, check=True)

    # Install anew
    print("Installing anew...")
    subprocess.run("go install -v github.com/tomnomnom/anew@latest", shell=True, check=True)

    # Install jq
    print("Installing jq...")
    subprocess.run("sudo DEBIAN_FRONTEND=noninteractive apt-get install -y jq", shell=True, check=True)

    # Install gau
    print("Installing gau...")
    subprocess.run("go install -v github.com/lc/gau/v2/cmd/gau@latest", shell=True, check=True)

    # Install dirsearch
    print("Installing dirsearch...")
    subprocess.run("git clone https://github.com/maurosoria/dirsearch.git", shell=True, check=True)
    subprocess.run("pip3 install -r dirsearch/requirements.txt", shell=True, check=True)

    # Install wordlist
    print("Installing wordlist...")
    subprocess.run("git clone https://github.com/six2dez/OneListForAll.git", shell=True, check=True)

    print("All tools installed successfully.")

# Function to run recon commands
def run_recon():
    domain_input = input("Enter the path to domains.txt file or a single domain: ")
    if os.path.isfile(domain_input):
        print(f"Using {domain_input} as input file.")
        target_domain = domain_input
    else:
        print(f"Using single domain: {domain_input}")
        target_domain = domain_input

    commands = [
        f"subfinder -dL {target_domain} -all -recursive -o subdomains.txt",
        f"curl -s https://crt.sh/?q={target_domain}&output=json | jq -r ' .[].name_value' | grep -Po '(\w+\.\w+\. \w+)$' | anew subdomains.txt",
        "cat subdomains.txt | httpx -1 -ports 443,80,8080,8000,8888 -threads 200 > subdomains_alive.txt",
        "naabu -list subdomains.txt -c 50 -nmap-cli 'nmap -SV -sC' -o naabu-full.txt",
        "dirsearch -l subdomains_alive.txt -x 500,502,429,404,400 -R 5 --random-agent -t 100 -F -o directory.txt -w /home/user/OneListForAll/shortlist.txt",
        "cat subdomains_alive.txt | gau > params.txt",
        "cat params.txt | uro -o filterparam.txt",
        "cat filterparam.txt | grep '.js$' > jsfiles.txt",
        "cat jsfiles.txt | uro | anew jsfiles.txt",
        "cat jsfiles.txt | while read url; do python3 /home/user/SecretFinder/SecretFinder.py -i $url -o cli >> secret.txt; done"
    ]

    print("Running reconnaissance commands...")
    for cmd in commands:
        print(f"Executing command: {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {cmd}\n{e}")
            return
    print("Reconnaissance completed.")

def main():
    install_tools()
    run_recon()

if __name__ == "__main__":
    main()
