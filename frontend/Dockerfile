# Use official Node.js runtime as base image
FROM node:20

# Set working directory
WORKDIR /app

# ---- IMPORTANT PART ----
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
# ------------------------

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy app source
COPY . .

# Build the app (env will be baked here)
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
