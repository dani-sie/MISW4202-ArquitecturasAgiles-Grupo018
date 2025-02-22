import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { Transport, MicroserviceOptions } from '@nestjs/microservices';

async function bootstrap() {
  // Create an HTTP-based NestJS application
  const app = await NestFactory.create(AppModule);

  // Connect the microservice with NATS transport
  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.NATS,
    options: {
      servers: ['nats://nats:4222'],  // Docker service name for NATS
    },
  });

  // Start both the microservice and the HTTP server
  await app.startAllMicroservices();
  await app.listen(3000);
  console.log(`Microservice is listening on port 3000 (HTTP) and connected to NATS`);
}
bootstrap();
