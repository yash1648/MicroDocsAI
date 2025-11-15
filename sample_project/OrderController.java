package com.example.microservices.order;

import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;

@RestController
@RequestMapping(value = "/api/v1/orders")
public class OrderController {
    
    @Autowired
    private OrderService orderService;
    
    @Autowired
    private PaymentClient paymentClient;
    
    @GetMapping
    public List<Order> getAllOrders() {
        return orderService.findAll();
    }
    
    @GetMapping("/{id}")
    public Order getOrderById(@PathVariable Long id) {
        return orderService.findById(id);
    }
    
    @PostMapping
    public Order createOrder(@RequestBody OrderRequest request) {
        return orderService.create(request);
    }
    
    @PutMapping("/{id}")
    public Order updateOrder(@PathVariable Long id, @RequestBody OrderRequest request) {
        return orderService.update(id, request);
    }
    
    @DeleteMapping("/{id}")
    public void deleteOrder(@PathVariable Long id) {
        orderService.delete(id);
    }
}