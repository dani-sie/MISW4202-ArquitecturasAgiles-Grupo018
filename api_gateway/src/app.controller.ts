import { Controller, Get } from '@nestjs/common';
import { MessagePattern, Payload } from '@nestjs/microservices';

@Controller()
export class AppController {
  // HTTP endpoint for basic health check
  @Get('health')
  getHealth() {
    return { status: 'healthy' };
  }

}
