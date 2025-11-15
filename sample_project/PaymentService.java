package com.example.microservices.payment;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class PaymentService {
    
    @Autowired
    private PaymentRepository paymentRepository;
    
    @Autowired
    private GatewayClient gatewayClient;
    
    public PaymentResponse process(PaymentRequest request) {
        Payment payment = new Payment(request);
        Payment saved = paymentRepository.save(payment);
        PaymentResponse response = gatewayClient.charge(saved);
        return response;
    }
    
    public PaymentStatus getStatus(String id) {
        Payment payment = paymentRepository.findById(id).orElse(null);
        return payment != null ? payment.getStatus() : null;
    }
    
    public RefundResponse refund(String id) {
        Payment payment = paymentRepository.findById(id).orElse(null);
        if (payment != null) {
            return gatewayClient.refund(payment);
        }
        return null;
    }
}