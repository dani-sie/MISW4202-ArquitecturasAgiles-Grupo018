import { Module } from '@nestjs/common';
import { NatsClientModule } from 'src/nats-client/nats-client.module';
import { UbicacionController } from './ubicacion.controller';

@Module({
  imports: [NatsClientModule],
  controllers: [UbicacionController],
  providers: [],
})
export class UbicacionModule {}