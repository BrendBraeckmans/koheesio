The framework architecture is built from a set of core components. Each of the implementations that the framework 
provides out of the box, can be swapped out for custom implementations as long as they match the API.

The core components are the following:
> <small>*Note:* click on the 'Concept' to take you to the corresponding module. The module documentation will have 
  greater detail on the specifics of the implementation</small>

## [**Step**](steps.md)

A custom unit of logic that can be executed. A Step is an atomic operation and serves as the building block of data 
pipelines built with the framework. A step can be seen as an operation on a set of inputs, and returns a set of 
outputs. This does not imply that steps are stateless (e.g. data writes)! This concept is visualized in the figure 
below.

```mermaid

flowchart LR

%% Should render like this
%% ┌─────────┐        ┌──────────────────┐        ┌─────────┐
%% │ Input 1 │───────▶│                  ├───────▶│Output 1 │
%% └─────────┘        │                  │        └─────────┘
%%                    │                  │
%% ┌─────────┐        │                  │        ┌─────────┐
%% │ Input 2 │───────▶│       Step       │───────▶│Output 2 │
%% └─────────┘        │                  │        └─────────┘
%%                    │                  │
%% ┌─────────┐        │                  │        ┌─────────┐
%% │ Input 3 │───────▶│                  ├───────▶│Output 3 │
%% └─────────┘        └──────────────────┘        └─────────┘

%% &nbsp; is for increasing the box size without having to mess with CSS settings
Step["
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;
&nbsp;
Step
&nbsp;
&nbsp;
&nbsp;
"]

I1["Input 1"] ---> Step
I2["Input 2"] ---> Step
I3["Input 3"] ---> Step

Step ---> O1["Output 1"]
Step ---> O2["Output 2"]
Step ---> O3["Output 3"]

```

Step is the core abstraction of the framework. Meaning, that it is the core building block of the framework and is used
to define all the operations that can be executed. 

Please see the [Step](steps.md) documentation for more details.

## [**Task**](tasks.md)

The unit of work of one execution of the framework. 

An execution usually consists of an `Extract - Transform - Load` approach of one data object.
Tasks typically consist of a series of Steps.

Please see the [Task](tasks.md) documentation for more details.

## [**Context**](context.md)

The Context is used to configure the environment where a Task or Step runs.

It is often based on configuration files and can be used to adapt behaviour of a Task or Step based on the environment
it runs in.

Please see the [Context](context.md) documentation for more details.

## [**logger**](logging.md)

A logger object to log messages with different levels.

Please see the [Logging](logging.md) documentation for more details.


The interactions between the base concepts of the model is visible in the below diagram:  

```mermaid
---
title: Koheesio Class Diagram
---
classDiagram
    Step .. Task
    Step .. Transformation
    Step .. Reader
    Step .. Writer

    class Context

    class LoggingFactory

    class Task{
        <<abstract>>
        + List~Step~ steps
        ...
        + execute() Output
    }

    class Step{
        <<abstract>>
        ...
        Output: ...
        + execute() Output
    }
    
    class Transformation{
        <<abstract>>
        + df: DataFrame
        ...
        Output:
        + df: DataFrame
        + transform(df: DataFrame) DataFrame
    }
    
    class Reader{
        <<abstract>>
        ...
        Output:
        + df: DataFrame
        + read() DataFrame
    }
    
    class Writer{
        <<abstract>>
        + df: DataFrame
        ...
        + write(df: DataFrame)
    }
```
