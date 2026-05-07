FROM node:18-alpine

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

RUN yarn build

CMD ["sh", "-c", "yarn preview --host 0.0.0.0 --port ${PORT:-3000}"] 