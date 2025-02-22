import { Module } from '@nestjs/common';
import { UbicacionMicroserviceController } from './app.controller';
import { NatsClientModule } from './nats-client/nats-client.module';
@Module({
  imports: [NatsClientModule],
  controllers: [UbicacionMicroserviceController],
  providers: [],
})
export class AppModule {}
