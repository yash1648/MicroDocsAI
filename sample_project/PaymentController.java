package com.example.microservices.payment;

import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;

@RestController
@RequestMapping(value = "/api/v1/payments")
public class PaymentController {
    
    @Autowired
    private PaymentService paymentService;
    
    @PostMapping
    public PaymentResponse processPayment(@RequestBody PaymentRequest request) {
        return paymentService.process(request);
    }
    
    @GetMapping("/{id}/status")
    public PaymentStatus getPaymentStatus(@PathVariable String id) {
        return paymentService.getStatus(id);
    }
    
    @PostMapping("/{id}/refund")
    public RefundResponse refundPayment(@PathVariable String id) {
        return paymentService.refund(id);
    }
}