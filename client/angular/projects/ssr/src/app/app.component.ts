import { Component, HostBinding, inject, OnInit, PLATFORM_ID, REQUEST } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  @HostBinding('class') class = 'h-full block';
}

