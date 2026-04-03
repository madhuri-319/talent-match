import { Component } from '@angular/core';
import { ChatbotComponent } from '../chatbot/chatbot.component';
import { JobMatchesComponent } from '../job-matches/job-matches.component';
import { ApplicationsComponent } from '../applications/applications.component';

@Component({
  selector: 'app-user-dashboard',
  standalone: true,
  imports: [
    ChatbotComponent,
    JobMatchesComponent,
    ApplicationsComponent
  ],
  templateUrl: './user-dashboard.component.html',
  styleUrls: ['./user-dashboard.component.scss']
})
export class UserDashboardComponent {}