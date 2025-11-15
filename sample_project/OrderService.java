package com.example.microservices.order;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;

@Service
public class OrderService {
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private NotificationService notificationService;
    
    public List<Order> findAll() {
        return orderRepository.findAll();
    }
    
    public Order findById(Long id) {
        return orderRepository.findById(id).orElse(null);
    }
    
    public Order create(OrderRequest request) {
        Order order = new Order(request);
        Order saved = orderRepository.save(order);
        notificationService.notifyOrderCreated(saved);
        return saved;
    }
    
    public Order update(Long id, OrderRequest request) {
        Order order = findById(id);
        order.update(request);
        return orderRepository.save(order);
    }
    
    public void delete(Long id) {
        orderRepository.deleteById(id);
    }
}