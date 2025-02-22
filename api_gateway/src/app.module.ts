import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { UbicacionController } from './ubicacion-ms/ubicacion.controller';
import { UbicacionModule } from './ubicacion-ms/ubicacion.module';

@Module({
  imports: [UbicacionModule],
  controllers: [AppController],
  providers: [],
})
export class AppModule {}
