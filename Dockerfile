FROM stimela/base:1.6.0
ENV SUCASA /casa-pipeline-release-5.6.1-8
ENV DIRCASA /casa
ENV CASAURL https://casa.nrao.edu/download/distro/casa-pipeline/release/el7/casa-pipeline-release-5.6.1-8.el7.tar.gz
RUN curl -L -o ${SUCASA}.tar.gz $CASAURL
RUN tar xzvf ${SUCASA}.tar.gz -C $SUCASA
RUN rm ${SUCASA}.tar.gz
ENV PATH /casa/casa-pipeline-release-5.6.1-8.el7/bin:$PATH
ADD . /Crasa
RUN pip install /Crasa
RUN python -c "import Crasa.crasa"
RUN casa --help
