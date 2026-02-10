FROM node:22.17
LABEL maintainer="esm@email.com"

# Never prompt the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Make app dir
RUN mkdir /app
WORKDIR /app

# Cache and install dependencies
COPY package.json .
COPY yarn.lock .
RUN yarn install

# Copy app files
COPY . .

ENV VITE_REACT_APP_API_URL=http://localhost:9000
EXPOSE 9000

# entrypoint
ENTRYPOINT ["/usr/bin/make"]
CMD ["start"]
