packer build \
--var IMAGE=anyscale/aviary:latest \
--var AMI_NAME=aviary-type-cpu-avdirdock2-k124 \
--var SOURCE_AMI=amazon-eks-node-1.24-* \
prepull-m5-aviary.pkr.hcl
 