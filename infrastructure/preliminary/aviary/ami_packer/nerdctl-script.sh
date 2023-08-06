sudo yum install amazon-ecr-credential-helper -y

# Configure Docker to use the credential helper.    
mkdir ~/.docker/
cat > ~/.docker/config.json << EOF
{
    "credsStore": "ecr-login"
}
EOF

# Download and install nerdctl.
wget https://github.com/containerd/nerdctl/releases/download/v0.23.0/nerdctl-0.23.0-linux-amd64.tar.gz
sudo tar Cxzvf /usr/bin nerdctl-0.23.0-linux-amd64.tar.gz

# containerd is not started when the machine is booted, so start it.
sudo systemctl start containerd

# The images used by Kubernetes with containerd reside in the
# k8s.io namespace, so create that. Not coterminous with
# the concept of a Kubernetes namespace.

##SA this seems to already exist for the non gpu one
#sudo nerdctl namespace create k8s.io

# Pull images with nerdctl to the k8s.io namespace.
# Since sudo is used, explicitly specify the location of the
# Docker config file, which nerdctl understands.
sudo DOCKER_CONFIG=/home/ec2-user/.docker/ nerdctl -n k8s.io pull --quiet $IMAGE

# Verify the containerd namespace and the images within it.
# ctr is the containerd CLI.
sudo ctr ns ls
sudo ctr -n k8s.io image ls