import { Controller, Get, Inject } from '@nestjs/common';
import { ClientProxy, MessagePattern, Payload } from '@nestjs/microservices';

@Controller()
export class UbicacionMicroserviceController {
  constructor(
    @Inject('NATS_SERVICE') private natsClient: ClientProxy,
  ) {}

  @Get('health')
  getHealth() {
    return { status: 'healthy' };
  }

  // Change to MessagePattern for request-response communication.
  @MessagePattern('ubicacionMock')
  async handleUbicacion(@Payload() ubicacionMockDto: { latitud: number; longitud: number; }): Promise<any> {
    console.log('Received payload:', ubicacionMockDto);
    // Process the payload and return the response directly.
    return {
      ...ubicacionMockDto,
      response: 'ubicacionMock created successfully',
    };
  }
}
