FROM node:24.21.0-alpine

WORKDIR /workspace
RUN npm install --global pnpm@12.8.1

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.base.json ./
COPY apps/api/package.json apps/api/package.json
COPY apps/web/package.json apps/web/package.json
RUN pnpm install --frozen-lockfile

COPY apps/web apps/web
ARG VITE_API_URL=http://localhost:3000
ENV VITE_API_URL=$VITE_API_URL
RUN pnpm --filter @quvetrail/web build

EXPOSE 4173
CMD ["pnpm", "--filter", "@quvetrail/web", "start"]
