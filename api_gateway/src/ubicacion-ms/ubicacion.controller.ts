import { Controller, Inject, Post, Body } from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';

@Controller('ubicacion')
export class UbicacionController   {
  constructor(@Inject('NATS_SERVICE') private natsClient: ClientProxy) {}

  @Post()
  getUbicacion(@Body() ubicacionMock: { latitud: number, longitud: number }) {
    return this.natsClient.send('ubicacionMock', ubicacionMock);
  }
}