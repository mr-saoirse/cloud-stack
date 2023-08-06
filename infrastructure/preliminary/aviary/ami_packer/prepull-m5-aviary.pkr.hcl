packer {
  required_plugins {
    amazon = {
      version = ">= 0.0.2"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "IMAGE" {
  type    = string
  default = "anyscale/aviary:latest"
}

variable "SOURCE_AMI" {
  type = string
  default = "amazon-eks-node-1.24-*"
}

variable "AMI_NAME" {
  type = string
}

source "amazon-ebs" "eks-ami" {
  ami_name             = "${var.AMI_NAME}"
  instance_type        = "m5.xlarge"
  region               = "us-east-1"
  iam_instance_profile = "control-plane.cluster-api-provider-aws.sigs.k8s.io"

  launch_block_device_mappings {
    device_name           = "/dev/xvda"
    volume_size           = 40
    volume_type           = "gp3"
    delete_on_termination = true
  }

  run_tag {
    key   = "team"
    value = "ai"
  }
  run_tag {
    key   = "app"
    value = "aviary"
  }
  run_tag {
    key   = "env"
    value = "prod"
  }

  source_ami_filter {
    filters = {
      name                = "${var.SOURCE_AMI}"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["602401143452"]
  }
  ssh_username = "ec2-user"
}

build {
  name = "ami-baker"
  sources = [
    "source.amazon-ebs.eks-ami"
  ]

  provisioner "shell" {
    environment_vars = [
      "IMAGE=${var.IMAGE}"
    ]

    script = "nerdctl-script.sh"
  }
}