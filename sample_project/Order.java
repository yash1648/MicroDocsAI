package com.example.microservices.order;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "orders")
public class Order {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private Long customerId;
    private BigDecimal totalAmount;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    public Order() {}
    
    public Order(OrderRequest request) {
        this.customerId = request.getCustomerId();
        this.totalAmount = request.getTotalAmount();
        this.status = "PENDING";
        this.createdAt = LocalDateTime.now();
    }
    
    public void update(OrderRequest request) {
        this.totalAmount = request.getTotalAmount();
        this.updatedAt = LocalDateTime.now();
    }
}
