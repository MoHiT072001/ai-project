package terraform_ai

default deny := []

deny[violation] {
  r := input.resources[_]
  r.resource_type == "aws_s3_bucket"
  public_bucket(r)
  violation := {
    "id": sprintf("opa:s3_public:%s", [r.address]),
    "severity": "high",
    "resource": r.address,
    "description": "S3 bucket may be publicly accessible (missing public access block or uses public ACL/policy patterns).",
    "recommendation": "Enable S3 Public Access Block, avoid public ACLs, and restrict bucket policies."
  }
}

deny[violation] {
  r := input.resources[_]
  r.resource_type == "aws_security_group"
  allows_world_ssh(r)
  violation := {
    "id": sprintf("opa:sg_world_ssh:%s", [r.address]),
    "severity": "critical",
    "resource": r.address,
    "description": "Security group allows SSH (22) from 0.0.0.0/0.",
    "recommendation": "Restrict SSH to known IP ranges or use SSM Session Manager / bastion with tight controls."
  }
}

deny[violation] {
  r := input.resources[_]
  missing_required_tags(r)
  violation := {
    "id": sprintf("opa:missing_tags:%s", [r.address]),
    "severity": "medium",
    "resource": r.address,
    "description": "Resource is missing required tags (Owner, Environment).",
    "recommendation": "Add required tags to all resources to support cost allocation, ownership, and governance."
  }
}

public_bucket(r) {
  acl := lower(object.get(r.attributes, "acl", ""))
  acl == "public-read" or acl == "public-read-write" or acl == "website"
}

public_bucket(r) {
  # If no public access block resource exists, flag as potential exposure (conservative MVP).
  not some pab in input.resources { pab.resource_type == "aws_s3_bucket_public_access_block" }
}

allows_world_ssh(r) {
  ingress := object.get(r.attributes, "ingress", [])
  some rule in as_array(ingress)
  port_22(rule)
  cidrs := object.get(rule, "cidr_blocks", [])
  some c in as_array(cidrs)
  c == "0.0.0.0/0"
}

port_22(rule) {
  object.get(rule, "from_port", -1) == 22
}

port_22(rule) {
  object.get(rule, "to_port", -1) == 22
}

missing_required_tags(r) {
  tags := object.get(r.attributes, "tags", {})
  not tags["Owner"]
}

missing_required_tags(r) {
  tags := object.get(r.attributes, "tags", {})
  not tags["Environment"]
}

as_array(x) = y {
  is_array(x)
  y := x
}

as_array(x) = y {
  not is_array(x)
  y := [x]
}

