FROM       openjdk:8-jdk-stretch

ENV HDFS_HOST hdfs://hdfs:9000

#ENV NEO4j_VERSION community-2.3.11
ENV NEO4j_VERSION enterprise-2.3.11

# Install Neo4j
RUN apt-get update && \
    apt-get install -y wget bzip2
#RUN wget -q -O /tmp/neo4j-$NEO4j_VERSION-unix.tar.gz http://dist.neo4j.org/neo4j-$NEO4j_VERSION-unix.tar.gz && \
RUN wget -O /tmp/neo4j-$NEO4j_VERSION-unix.tar.gz https://neo4j.com/artifact.php?name=neo4j-$NEO4j_VERSION-unix.tar.gz && \
    tar -zxf /tmp/neo4j-$NEO4j_VERSION-unix.tar.gz -C /var/lib && \
    ln -s /var/lib/neo4j-$NEO4j_VERSION /var/lib/neo4j
    # wget -O /var/lib/neo4j/lib/gson-2.2.4.jar http://search.maven.org/remotecontent?filepath=com/google/code/gson/gson/2.2.4/gson-2.2.4.jar

WORKDIR /var/lib/neo4j

# Copy graph analytics plugin
COPY ./compose/graphdb/neo4j/plugins /var/lib/neo4j/plugins

# Copy configurations
COPY ./compose/graphdb/neo4j/conf /var/lib/neo4j/conf

# Copy the bootstrap shell script and set permissions
# COPY sbin/bootstrap.sh /etc/bootstrap.sh
#RUN chown root:root /etc/bootstrap.sh && \
#    chmod 700 /etc/bootstrap.sh

# Expose the Neo4j browser to the host OS on port 7474 and 1337
EXPOSE 7474
EXPOSE 1337


RUN rm -rf /usr/local/miniconda && curl -sSLO https://repo.continuum.io/miniconda/Miniconda3-4.2.12-Linux-x86_64.sh && \
    bash Miniconda3-4.2.12-Linux-x86_64.sh -b -p /usr/local/miniconda && \
    rm Miniconda3-4.2.12-Linux-x86_64.sh
ENV PATH=/usr/local/miniconda/bin:$PATH

# Create conda environment
RUN conda config --add channels conda-forge && \
    conda install -y pandas 
RUN pip install cognitiveatlas "py2neo<3"

#RUN mkdir /code
#ADD . /code
#WORKDIR /code
#RUN bash scripts/docker_import.sh

# make invalid rrd so neo attempts to replace it instead of defaulting to datadir
RUN mkdir /rrd/
RUN touch /rrd/rrd
# Mount a volume for persistent data
VOLUME /opt/data
VOLUME /rrd/

# Set the bootstrap script on container run
CMD ["/var/lib/neo4j/bin/neo4j", "console", "-d"]
