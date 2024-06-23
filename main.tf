provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "app_instance" {
  ami           = "ami-0c55b159cbfafe1f0" # Välj en lämplig AMI för din region
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.app_sg.id]

  tags = {
    Name = "AppInstance"
  }
}

resource "aws_security_group" "app_sg" {
  name_prefix = "app-sg-"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "jenkins_instance" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.jenkins_sg.id]

  tags = {
    Name = "JenkinsInstance"
  }
}

resource "aws_security_group" "jenkins_sg" {
  name_prefix = "jenkins-sg-"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
