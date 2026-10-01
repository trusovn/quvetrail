FROM node:24.21.0-alpine

WORKDIR /workspace
RUN npm install --global pnpm@12.8.1

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.base.json ./
COPY apps/api/package.json apps/api/package.json
COPY apps/web/package.json apps/web/package.json
RUN pnpm install --frozen-lockfile

COPY apps/api apps/api
RUN pnpm --filter @quvetrail/api build

EXPOSE 3000
CMD ["sh", "-c", "pnpm --filter @quvetrail/api db:migrate && node apps/api/dist/server.js"]
