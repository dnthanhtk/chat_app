FROM node

WORKDIR /app/frontend
# COPY package.json /app/frontend
COPY . /app/frontend/

RUN npm install -g npm@6.14.13
RUN npm install react-scripts@1.1.1 -g --silent
RUN npm install axios --save
RUN npm install

CMD ["npm", "start"]
