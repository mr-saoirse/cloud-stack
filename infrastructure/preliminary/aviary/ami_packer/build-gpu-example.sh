packer build \
--var IMAGE=anyscale/aviary:latest \
--var AMI_NAME=aviary-type-gpu-avdirdock-k124 \
--var SOURCE_AMI=amazon-eks-gpu-node-1.24-* \
prepull-m5-aviary.pkr.hcl
