package com.example.microservices.notification;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class NotificationService {
    
    private RestTemplate restTemplate = new RestTemplate();
    
    public void notifyOrderCreated(Order order) {
        String notification = "Order " + order.getId() + " has been created";
        sendNotification(notification, order.getCustomerId());
    }
    
    public void notifyPaymentProcessed(Payment payment) {
        String notification = "Payment " + payment.getId() + " processed successfully";
        sendNotification(notification, payment.getCustomerId());
    }
    
    private void sendNotification(String message, Long customerId) {
        // Send via message queue or email
    }
}
